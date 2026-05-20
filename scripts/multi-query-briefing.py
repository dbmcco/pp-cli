#!/usr/bin/env python3

# ABOUTME: Multi-query morning briefing - runs separate queries per section

import subprocess
import sys
import os
import re
import shutil
import urllib.request
import json
from datetime import datetime
from pathlib import Path

DEFAULT_PP_PATH = Path('/opt/homebrew/bin/pp')
PP_CLI_HELP_TIMEOUT_SECONDS = 5.0


def build_pp_cli_error(detail: str) -> str:
    return (
        f"{detail} "
        "Expected the Perplexity CLI (supports '--no-interactive' and '--output'). "
        "Set PP_CLI_PATH to the correct Perplexity binary."
    )


def validate_pp_cli(candidate: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [candidate, "--help"],
            capture_output=True,
            text=True,
            timeout=PP_CLI_HELP_TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        return False, build_pp_cli_error(f"Configured PP_CLI_PATH does not exist: {candidate!r}.")
    except subprocess.TimeoutExpired:
        return False, build_pp_cli_error(f"Timed out while probing CLI help for {candidate!r}.")
    except Exception as e:
        return False, build_pp_cli_error(f"Failed to probe CLI {candidate!r}: {e}.")

    help_text = f"{result.stdout}\n{result.stderr}"
    if "Pretty prints a file containing ASN.1 data" in help_text:
        return False, build_pp_cli_error(f"`{candidate}` is NSS `pp`, not Perplexity CLI.")
    if "--no-interactive" in help_text and "--output" in help_text:
        return True, ""
    return False, build_pp_cli_error(f"`{candidate}` does not expose Perplexity CLI flags.")


def resolve_pp_cli() -> tuple[str | None, str]:
    configured = os.environ.get("PP_CLI_PATH")
    if configured:
        is_valid, error = validate_pp_cli(configured)
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
        return None, build_pp_cli_error("Unable to locate a `pp` binary on PATH.")

    first_error = ""
    for candidate in candidates:
        is_valid, error = validate_pp_cli(candidate)
        if is_valid:
            return candidate, ""
        if not first_error:
            first_error = error

    return None, first_error or build_pp_cli_error("Unable to validate pp CLI.")


PP_CLI, PP_CLI_ERROR = resolve_pp_cli()
if not PP_CLI:
    print(f"Error: {PP_CLI_ERROR}", file=sys.stderr)
    sys.exit(1)

def run_query(query: str) -> tuple[str, list[tuple[str, str]]]:
    """Run a single pp query and return (content, citations) tuple"""
    try:
        result = subprocess.run(
            [PP_CLI, '--no-interactive', query, '--output', 'markdown'],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Log any errors from stderr
        if result.stderr:
            print(f"Query stderr: {result.stderr[:200]}", file=sys.stderr)

        # Log return code if non-zero
        if result.returncode != 0:
            print(f"Query failed with return code {result.returncode}", file=sys.stderr)
            print(f"stdout: {result.stdout[:500]}", file=sys.stderr)
            return "", []

        # Filter out progress indicators
        lines = result.stdout.split('\n')
        content = '\n'.join(line for line in lines
                          if not line.startswith(('- ', 'Searching', 'Thinking')))

        # Split content from citations
        if '## Sources' in content:
            parts = content.split('## Sources', 1)
            main_content = parts[0].strip()
            sources_section = parts[1].strip()

            # Extract citations from sources section
            citations = []
            for line in sources_section.split('\n'):
                # Match pattern: 1. [domain.com](url)
                match = re.match(r'\d+\.\s+\[([^\]]+)\]\(([^\)]+)\)', line)
                if match:
                    citations.append((match.group(1), match.group(2)))

            return main_content, citations

        return content.strip(), []
    except Exception as e:
        print(f"Error running query: {e}", file=sys.stderr)
        return "", []

def parse_queries_file(file_path: str) -> list[tuple[str, str]]:
    """Parse the queries file into (section_name, query) tuples"""
    queries = []
    current_section = None
    current_query = []

    with open(file_path, 'r') as f:
        for line in f:
            line = line.rstrip()

            if line.startswith('SECTION:'):
                # Save previous section if exists
                if current_section and current_query:
                    queries.append((current_section, '\n'.join(current_query)))

                # Start new section
                current_section = line.split(':', 1)[1].strip()
                current_query = []
            elif current_section and line:  # Non-empty line in a section
                current_query.append(line)

        # Don't forget the last section
        if current_section and current_query:
            queries.append((current_section, '\n'.join(current_query)))

    return queries

def renumber_citations(content: str, citation_map: dict[int, int]) -> str:
    """Renumber citations in content according to citation_map"""
    # Replace [N] with new numbers
    def replace_cite(match):
        old_num = int(match.group(1))
        new_num = citation_map.get(old_num, old_num)
        return f'[{new_num}]'

    return re.sub(r'\[(\d+)\]', replace_cite, content)

def get_weather() -> str:
    """Get weather from weather.gov API for Old Lyme, CT (no API key required)"""
    try:
        # Old Lyme, CT coordinates
        lat, lon = 41.3184, -72.3254

        # Step 1: Get the forecast office and grid coordinates
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        req = urllib.request.Request(
            points_url,
            headers={'User-Agent': 'BraydonMorningBriefing/1.0 (braydon@example.com)'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            points_data = json.loads(response.read().decode('utf-8'))

        forecast_url = points_data['properties']['forecast']

        # Step 2: Get the forecast
        req = urllib.request.Request(
            forecast_url,
            headers={'User-Agent': 'BraydonMorningBriefing/1.0 (braydon@example.com)'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            forecast_data = json.loads(response.read().decode('utf-8'))

        periods = forecast_data['properties']['periods']

        # Build compact weather string
        lines = []
        for i, period in enumerate(periods[:4]):  # Today, Tonight, Tomorrow, Tomorrow Night
            name = period['name']
            temp = period['temperature']
            unit = period['temperatureUnit']
            short = period['shortForecast']
            wind = period.get('windSpeed', '')
            wind_dir = period.get('windDirection', '')

            if i == 0:
                lines.append(f"{name}: {temp}°{unit}, {short}, Wind {wind_dir} {wind}")
            else:
                lines.append(f"{name}: {temp}°{unit}, {short}")

        return '\n'.join(lines)

    except Exception as e:
        print(f"Warning: Could not fetch weather from weather.gov: {e}", file=sys.stderr)
        # Fallback to wttr.in
        try:
            url = "https://wttr.in/Old+Lyme,CT?format=%l:+%C+%t+%w"
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.read().decode('utf-8').strip()
        except:
            return "Weather data unavailable"

def main():
    # Get script directory and dates
    script_dir = Path(__file__).parent
    today = datetime.now().strftime('%Y-%m-%d')
    briefing_date = datetime.now().strftime('%A, %B %d, %Y')
    day_of_week = datetime.now().strftime('%A').lower()

    # Paths
    queries_file = script_dir / 'prompts' / f'{day_of_week}-queries.md'
    vault_path = Path('/Users/braydon/Obsidian/Bvault/Daily notes') / f'{today}.md'

    # Check if queries file exists
    if not queries_file.exists():
        print(f"Error: Queries file not found: {queries_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Generating briefing for {briefing_date}...")

    # Parse queries
    queries = parse_queries_file(str(queries_file))

    # Get weather first from wttr.in API (not a query)
    print(f"  Fetching weather...")
    weather_content = get_weather()

    # Run each query and collect all citations
    results = []
    all_citations = []

    for section_name, query in queries:
        # Skip weather section - we already have it from API
        if 'weather' in section_name.lower():
            continue

        print(f"  Querying: {section_name}...")
        content, citations = run_query(query)

        if content:
            # Build citation map for this section
            citation_map = {}
            section_citations = []

            for i, (domain, url) in enumerate(citations, 1):
                # Check if we already have this citation
                global_idx = None
                for idx, (d, u) in enumerate(all_citations, 1):
                    if u == url:
                        global_idx = idx
                        break

                if global_idx is None:
                    # New citation
                    all_citations.append((domain, url))
                    global_idx = len(all_citations)

                citation_map[i] = global_idx

            # Renumber citations in content
            content = renumber_citations(content, citation_map)
            results.append((section_name, content))

    # Combine into final note
    print("Appending to daily note...")

    vault_path.parent.mkdir(parents=True, exist_ok=True)

    # Build the briefing content to append
    briefing_content = []
    briefing_content.append('\n---\n')
    briefing_content.append(f'## Morning Briefing - {briefing_date}\n\n')

    # Weather first (compact)
    if weather_content:
        briefing_content.append(f'**Weather** (Old Lyme, CT): {weather_content}\n\n')

    # All other sections
    for section_name, content in results:
        briefing_content.append(f'### {section_name}\n\n')
        briefing_content.append(f'{content}\n\n')

    # References at the bottom
    if all_citations:
        briefing_content.append('### References\n\n')
        for i, (domain, url) in enumerate(all_citations, 1):
            briefing_content.append(f'{i}. [{domain}]({url})\n')

    # Append to existing daily note or create if doesn't exist
    if vault_path.exists():
        with open(vault_path, 'a') as f:
            f.write(''.join(briefing_content))
    else:
        # Create new daily note with minimal frontmatter
        with open(vault_path, 'w') as f:
            f.write('---\n')
            f.write('tags:\n')
            f.write('  - daily\n')
            f.write('---\n')
            f.write(''.join(briefing_content))

    print(f"✓ Briefing appended to: Daily notes/{today}.md")

if __name__ == '__main__':
    main()
