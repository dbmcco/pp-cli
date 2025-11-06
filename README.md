# pp-cli

A conversational command-line interface for Perplexity AI with beautiful terminal output and Obsidian note integration.

## Features

- **Conversational by default** - Interactive queries with context preservation
- **Beautiful formatting** - Markdown rendering with syntax highlighting and clickable links
- **Research mode** - Deep analysis with the `sonar-reasoning` model
- **Obsidian integration** - Save conversations as formatted markdown notes
- **Automated briefings** - Daily personalized news summaries delivered to your vault
- **Claude Code integration** - Non-interactive mode with JSON/markdown output for programmatic use
- **Smart retry logic** - Handles rate limits and network errors gracefully

## Quick Start

### Installation

```bash
npm install -g pp-cli
```

### Configuration

```bash
pp config
```

You'll be prompted for:
- **Perplexity API Key** - Get one at [perplexity.ai](https://www.perplexity.ai/)
- **Obsidian Vault Path** - Path to your searches directory (e.g., `/Users/you/vault/searches`)
- **Default Model** - Press Enter for `sonar-pro`

Config is stored at `~/.config/pp/config.json`

### Basic Usage

```bash
# Start a conversation
pp rust ownership
> how does it differ from garbage collection
> show me an example with a vector
> exit
Save to vault? (y/n): y
✓ Saved to: 2025-11-06-rust-ownership-basics.md

# Deep research mode
pp -r latest advances in quantum computing
> what are the main challenges
> exit

# Non-interactive (for scripts)
pp --no-interactive "explain async/await" --output json
```

## Interactive Mode

Every query starts an interactive conversation where you can ask follow-up questions.

### Features

- Full conversation context preserved across questions
- Type `exit` or `quit` to end the session
- Prompted to save the full conversation to Obsidian
- Responses stream with beautiful markdown formatting
- Citations displayed with clickable links

### Example

```bash
pp capital of france
> what about the history
> when was the eiffel tower built
> exit
Save to vault? y
```

**Note about contractions:** Wrap queries with contractions in quotes:
```bash
pp "what's the difference between rust and c++"
```

## Research Mode

Use the `-r` flag for comprehensive research with the `sonar-reasoning` model:

```bash
pp -r "latest advances in fusion energy"
> what are the main challenges
> compare inertial vs magnetic confinement
> exit
```

**Research mode provides:**
- More detailed, comprehensive responses using advanced reasoning
- "Thinking deeply..." indicator during processing
- Better for in-depth analysis and complex topics
- Same interactive experience with context preservation

## Obsidian Integration

### Saving Conversations

When you save a conversation, pp-cli creates a markdown note with:

- **YAML frontmatter** - Timestamp, original query, tags
- **Q&A format** - Clear question and answer structure
- **Full conversation** - Every question and response
- **Sources section** - All citations with clickable links

### Example Note

```markdown
---
created: 2025-11-06T10:30:00Z
query: "explain quantum computing"
tags: [perplexity, search]
---

# Quantum Computing Basics

**Q:** explain quantum computing
**A:** Quantum computing leverages quantum mechanics...

---

**Q:** how does it differ from classical computing
**A:** Classical computers use bits (0 or 1)...

---

## Sources
- [Quantum Computing Explained](https://example.com)
- [IBM Quantum](https://quantum-computing.ibm.com)
```

### Programmatic Saving

```bash
# Save to specific note
pp --no-interactive "TypeScript best practices" --save-to "dev/typescript.md"

# Append to existing note
pp --no-interactive "advanced TypeScript patterns" --append-to "dev/typescript.md"
```

## Automated Morning Briefing

Generate personalized daily news summaries automatically to your Obsidian vault.

### What You Get

- **Day-specific content** - Different sections for each day of the week
- **Intelligence briefing style** - Bulleted headlines with concise summaries
- **Personalized topics** - GenAI/LLM, tech industry, Hacker News, electric vehicles, classical music
- **Weather** - Location-specific forecast at the top
- **Citation management** - Global numbering with consolidated references

### Quick Setup

1. **Test the briefing manually:**
   ```bash
   cd /Users/braydon/projects/experiments/pp
   ./scripts/run-morning-briefing.sh
   ```

2. **Set up automated daily run (5 AM):**
   ```bash
   echo "0 5 * * * /Users/braydon/projects/experiments/pp/scripts/run-morning-briefing.sh >> /tmp/morning-briefing.log 2>&1" | crontab -
   ```

3. **Verify cron job:**
   ```bash
   crontab -l
   ```

### Daily Content Breakdown

- **Monday**: Week Ahead Preview, Weekend Recap, GenAI/LLM, Tech & Business
- **Tuesday**: Top Headlines, Business & Markets, GenAI/LLM, Tech Industry
- **Wednesday**: Top Headlines, GenAI Deep Dive (narrative), Tech Industry
- **Thursday**: Top Headlines, GenAI/LLM, Tech Industry, Electric Vehicles
- **Friday**: Week in Review, GenAI Weekly Wrap, Hacker News Top Stories
- **Saturday**: Week in Review, GenAI Deep Dive, Hacker News Weekly, Classical Music
- **Sunday**: Week Ahead Preview, Weekend Headlines, Classical Music, Markets Preview

### Output Location

Briefings are saved to: `/Users/braydon/Obsidian/Bvault/daily-briefings/YYYY-MM-DD-news-briefing.md`

Each briefing includes:
- YAML frontmatter with date and metadata
- Weather at the top (location-specific)
- Bulleted sections with bold headlines
- Consolidated references at the bottom

### Customization

Edit query files in `scripts/prompts/{day}-queries.md` to customize:
- Section topics and focus areas
- Location for weather
- News sources and balance (left/center/right)
- Time ranges (THIS WEEK, TODAY, etc.)
- Output formatting requirements

## Programmatic Usage

Use non-interactive mode for scripting and Claude Code integration.

### Output Formats

```bash
# Get JSON output for parsing
pp --no-interactive "what is rust ownership" --output json

# Get raw markdown
pp --no-interactive "explain TypeScript generics" --output markdown

# Get plain text (default)
pp --no-interactive "Node.js advantages" --output text
```

### JSON Output Format

```json
{
  "query": "what is rust ownership",
  "answer": "**Rust ownership** is a compile-time system...",
  "citations": [
    "https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html",
    "https://www.w3schools.com/rust/rust_ownership.php"
  ],
  "model": "sonar-pro"
}
```

### Available Flags

- `--no-interactive` - Skips follow-up prompts (for scripting)
- `--output <format>` - Choose `text`, `json`, or `markdown`
- `--save-to <path>` - Save to specific note path (relative to vault)
- `--append-to <path>` - Append to existing note
- `-r` - Use research mode with `sonar-reasoning` model

### Examples

```bash
# Non-interactive with JSON output (for Claude Code)
pp --no-interactive "explain async/await in JavaScript" --output json

# Save directly to specific note
pp --no-interactive "TypeScript best practices" --save-to "dev/typescript.md"

# Append follow-up to existing note
pp --no-interactive "advanced TypeScript patterns" --append-to "dev/typescript.md"

# Research mode with JSON output
pp -r --no-interactive "quantum computing" --output json
```

## Terminal Features

- **Markdown Rendering** - Headers, lists, code blocks properly formatted
- **Syntax Highlighting** - Code blocks with language-specific colors
- **Clickable Links** - CMD+click URLs to open (in supported terminals like iTerm2)
- **Beautiful Citations** - Numbered sources with clickable links
- **Progress Indicators** - Visual feedback during processing

## Commands Reference

```
pp [query...]                           Start interactive conversation
pp -r [query...]                        Deep research mode with reasoning model
pp --no-interactive [query...]          Non-interactive mode for scripting
pp --output <format> [query...]         Choose output format (text|json|markdown)
pp --save-to <path> [query...]          Save to specific Obsidian note
pp --append-to <path> [query...]        Append to existing note
pp config                               Configure API key and vault path
pp --version                            Show version
pp --help                               Show help
```

## Requirements

- **Node.js** >= 18
- **Perplexity API key** - Required for all searches
- **Obsidian vault** - Optional, only needed for saving notes

## Development

Clone and build from source:

```bash
git clone https://github.com/dbmcco/pp-cli.git
cd pp-cli
npm install
npm run build
npm link
```

Run tests:
```bash
npm test
```

## License

MIT
