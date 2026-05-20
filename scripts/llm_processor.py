#!/Users/braydon/projects/experiments/pp/scripts/venv/bin/python3

# ABOUTME: LLM processing layer for RSS content summarization
# ABOUTME: Supports Perplexity (pp CLI) and Claude API for synthesis

import subprocess
import sys
import os
import shutil
import json
from pathlib import Path
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # dotenv not available, rely on system environment

# Try to import anthropic for Claude API
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

# Try to import openai for DeepSeek API (OpenAI-compatible)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Locate pp CLI
DEFAULT_PP_PATH = Path('/opt/homebrew/bin/pp')
PP_CLI_HELP_TIMEOUT_SECONDS = 5.0


def _build_pp_cli_error(detail: str) -> str:
    return (
        f"{detail} "
        "Expected the Perplexity CLI (supports '--no-interactive' and '--output'). "
        "Set PP_CLI_PATH in scripts/.env to the correct Perplexity binary."
    )


def _validate_pp_cli(candidate: str) -> tuple[bool, str]:
    """Return (is_valid, error_message) for a candidate pp CLI binary."""
    try:
        result = subprocess.run(
            [candidate, "--help"],
            capture_output=True,
            text=True,
            timeout=PP_CLI_HELP_TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        return False, _build_pp_cli_error(f"Configured PP_CLI_PATH does not exist: {candidate!r}.")
    except subprocess.TimeoutExpired:
        return False, _build_pp_cli_error(
            f"Timed out while probing CLI help for {candidate!r}."
        )
    except Exception as e:
        return False, _build_pp_cli_error(f"Failed to probe CLI {candidate!r}: {e}.")

    help_text = f"{result.stdout}\n{result.stderr}"
    if "Pretty prints a file containing ASN.1 data" in help_text:
        return False, _build_pp_cli_error(
            f"`{candidate}` is NSS `pp` (ASN.1 utility), not Perplexity CLI."
        )

    if "--no-interactive" in help_text and "--output" in help_text:
        return True, ""

    return False, _build_pp_cli_error(
        f"`{candidate}` does not expose Perplexity CLI flags."
    )


def _resolve_pp_cli() -> tuple[Optional[str], str]:
    configured = os.environ.get("PP_CLI_PATH")
    if configured:
        is_valid, error = _validate_pp_cli(configured)
        if is_valid:
            return configured, ""
        return None, error

    candidates = []
    if DEFAULT_PP_PATH.exists():
        candidates.append(str(DEFAULT_PP_PATH))
    path_match = shutil.which("pp")
    if path_match and path_match not in candidates:
        candidates.append(path_match)

    if not candidates:
        return None, _build_pp_cli_error(
            "Unable to locate a `pp` binary. No PP_CLI_PATH configured and none found on PATH."
        )

    first_error = ""
    for candidate in candidates:
        is_valid, error = _validate_pp_cli(candidate)
        if is_valid:
            return candidate, ""
        if not first_error:
            first_error = error

    return None, first_error or _build_pp_cli_error("Unable to validate pp CLI.")


PP_CLI, PP_CLI_ERROR = _resolve_pp_cli()


def _read_positive_float_env(name: str, default: float) -> float:
    """Read a positive float env var, falling back to default on invalid values."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError:
        print(f"Warning: invalid {name}={raw!r}; using default {default}", file=sys.stderr)
        return default
    if value <= 0:
        print(f"Warning: {name} must be > 0; using default {default}", file=sys.stderr)
        return default
    return value


PP_CLI_TIMEOUT_SECONDS = _read_positive_float_env("PP_CLI_TIMEOUT_SECONDS", 180.0)


def summarize_with_perplexity(content: str, prompt: str) -> str:
    """Use Perplexity (pp CLI) to summarize/augment content"""
    if not PP_CLI:
        print(f"Error: {PP_CLI_ERROR}", file=sys.stderr)
        return ""

    full_prompt = f"""{prompt}

Here is the source content to process:

{content}"""

    try:
        result = subprocess.run(
            [PP_CLI, '--no-interactive', full_prompt, '--output', 'markdown'],
            capture_output=True,
            text=True,
            timeout=PP_CLI_TIMEOUT_SECONDS
        )

        if result.returncode != 0:
            print(f"pp CLI error: {result.stderr[:200]}", file=sys.stderr)
            return ""

        # Filter progress indicators
        lines = result.stdout.split('\n')
        filtered = '\n'.join(
            line for line in lines
            if not line.startswith(('- ', 'Searching', 'Thinking'))
        )

        # Keep sources section - citations are valuable!
        return filtered.strip()

    except subprocess.TimeoutExpired:
        print(f"pp CLI timed out after {PP_CLI_TIMEOUT_SECONDS:.0f}s", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"pp CLI error: {e}", file=sys.stderr)
        return ""


def summarize_with_claude(content: str, prompt: str, model: str = "claude-haiku-4-5-20251001") -> str:
    """Use Claude API to summarize content"""
    if not CLAUDE_AVAILABLE:
        print("Warning: anthropic package not installed", file=sys.stderr)
        return ""

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("Warning: ANTHROPIC_API_KEY not set", file=sys.stderr)
        return ""

    try:
        client = anthropic.Anthropic(api_key=api_key)

        full_prompt = f"""{prompt}

Here is the source content to process:

{content}"""

        message = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )

        return message.content[0].text.strip()

    except Exception as e:
        print(f"Claude API error: {e}", file=sys.stderr)
        return ""


def summarize_with_deepseek(content: str, prompt: str, model: str = "deepseek-chat") -> str:
    """Use DeepSeek API to summarize content (OpenAI-compatible)"""
    if not OPENAI_AVAILABLE:
        print("Warning: openai package not installed", file=sys.stderr)
        return ""

    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        print("Warning: DEEPSEEK_API_KEY not set", file=sys.stderr)
        return ""

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        full_prompt = f"""{prompt}

Here is the source content to process:

{content}"""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=1024,
            stream=False
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"DeepSeek API error: {e}", file=sys.stderr)
        return ""


def strip_meta_framing(content: str) -> str:
    """Remove conversational framing if present"""
    lines = content.split('\n')
    filtered = []
    for line in lines:
        # Skip lines that are meta-commentary
        stripped = line.strip()
        if stripped.startswith(('Based on', 'Here are', 'Here is', 'The following',
                                'I have selected', 'From the provided', 'According to')):
            continue
        filtered.append(line)
    return '\n'.join(filtered)


def augment_with_perplexity(headlines: str, augment_prompt: str) -> str:
    """Use Perplexity to get additional web context for a topic"""
    if not PP_CLI:
        print(f"Error: {PP_CLI_ERROR}", file=sys.stderr)
        return ""

    # Insert headlines into the augment prompt
    prompt = augment_prompt.format(headlines=headlines)

    try:
        result = subprocess.run(
            [PP_CLI, '--no-interactive', prompt, '--output', 'markdown'],
            capture_output=True,
            text=True,
            timeout=PP_CLI_TIMEOUT_SECONDS
        )

        if result.returncode != 0:
            return ""

        # Filter and clean
        lines = result.stdout.split('\n')
        filtered = '\n'.join(
            line for line in lines
            if not line.startswith(('- ', 'Searching', 'Thinking'))
        )

        # Keep sources section - citations are valuable!
        return filtered.strip()

    except subprocess.TimeoutExpired:
        print(f"pp CLI augmentation timed out after {PP_CLI_TIMEOUT_SECONDS:.0f}s", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"Augmentation error: {e}", file=sys.stderr)
        return ""


def format_rss_as_bullets(content: str, max_items: int = 5) -> str:
    """
    Format RSS content directly as bullet points without LLM.
    Used as fallback when Claude is unavailable and Perplexity won't work for summarization.
    """
    lines = content.strip().split('\n')
    bullets = []
    current_item = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # New item starts with number
        if line[0].isdigit() and '. [' in line:
            if current_item and len(bullets) < max_items:
                # Format previous item
                title = current_item.get('title', '')
                summary = current_item.get('summary', '')
                source = current_item.get('source', '')
                if title:
                    bullet = f"• **{title}**"
                    if summary:
                        bullet += f": {summary[:150]}..."
                    if source:
                        bullet += f" [{source}]"
                    bullets.append(bullet)

            # Parse new item: "1. [Source] Title"
            try:
                rest = line.split('. ', 1)[1]
                if rest.startswith('['):
                    source_end = rest.index(']')
                    source = rest[1:source_end]
                    title = rest[source_end + 2:].strip()
                else:
                    source = ""
                    title = rest
                current_item = {'title': title, 'source': source}
            except (IndexError, ValueError):
                current_item = {'title': line}

        elif line.startswith('Summary:'):
            current_item['summary'] = line[8:].strip()

    # Don't forget last item
    if current_item and len(bullets) < max_items:
        title = current_item.get('title', '')
        summary = current_item.get('summary', '')
        source = current_item.get('source', '')
        if title:
            bullet = f"• **{title}**"
            if summary:
                bullet += f": {summary[:150]}..."
            if source:
                bullet += f" [{source}]"
            bullets.append(bullet)

    return '\n'.join(bullets)


def process_rss_content(
    content: str,
    summary_prompt: str,
    use_perplexity: bool = False,
    use_deepseek: bool = True,
    use_claude: bool = False,
    augment_prompt: Optional[str] = None,
) -> tuple[str, Optional[str]]:
    """
    Process RSS content through LLM pipeline.

    Returns: (summary, augmentation) tuple

    Note: Perplexity always does web search, so it can't summarize provided content.
    For pure summarization, DeepSeek or Claude API is required. Without it, we format RSS directly.
    """
    summary = ""
    augmentation = None

    # Primary summarization - try DeepSeek first, then Claude
    # (Perplexity always searches the web instead of summarizing provided content)
    if use_deepseek and OPENAI_AVAILABLE and os.environ.get('DEEPSEEK_API_KEY'):
        print("    Using DeepSeek for summarization...", file=sys.stderr)
        summary = summarize_with_deepseek(content, summary_prompt)
        # Strip meta-framing from summary
        if summary:
            summary = strip_meta_framing(summary)
    elif use_claude and CLAUDE_AVAILABLE and os.environ.get('ANTHROPIC_API_KEY'):
        print("    Using Claude for summarization...", file=sys.stderr)
        summary = summarize_with_claude(content, summary_prompt)
        # Strip meta-framing from summary
        if summary:
            summary = strip_meta_framing(summary)

    # Fallback: format RSS items directly without LLM
    if not summary:
        print("    LLM unavailable - formatting RSS directly...", file=sys.stderr)
        summary = format_rss_as_bullets(content)

    # Optional augmentation with Perplexity web search
    # This is where Perplexity shines - finding additional context
    if augment_prompt and PP_CLI:
        print("    Augmenting with Perplexity web search...", file=sys.stderr)
        # Extract just headlines for the augmentation prompt
        headlines = '\n'.join(
            line for line in content.split('\n')
            if line.strip() and not line.startswith(('   ', 'Summary:', 'Link:', 'Date:'))
        )
        augmentation = augment_with_perplexity(headlines, augment_prompt)
    elif augment_prompt and not PP_CLI:
        print(f"    Skipping Perplexity augmentation: {PP_CLI_ERROR}", file=sys.stderr)

    return summary, augmentation


# Quick test
if __name__ == '__main__':
    print("Testing LLM processor...")
    print(f"PP CLI available: {bool(PP_CLI)}")
    if not PP_CLI:
        print(f"PP CLI error: {PP_CLI_ERROR}")
    print(f"DeepSeek available: {OPENAI_AVAILABLE and bool(os.environ.get('DEEPSEEK_API_KEY'))}")
    print(f"Claude available: {CLAUDE_AVAILABLE and bool(os.environ.get('ANTHROPIC_API_KEY'))}")

    test_content = """
1. [NPR] Major earthquake strikes Pacific region
   Summary: A 7.2 magnitude earthquake hit the Pacific coast early today.
   Date: 2025-11-30 08:00

2. [BBC] Global climate summit reaches historic agreement
   Summary: World leaders agree to new emissions targets at COP30.
   Date: 2025-11-30 06:00
"""

    test_prompt = """Select the most important story and format as:
• **Headline**: Brief summary."""

    summary, _ = process_rss_content(test_content, test_prompt, use_deepseek=True)
    print(f"\nResult:\n{summary}")
