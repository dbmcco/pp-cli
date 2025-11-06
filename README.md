# pp-cli

A conversational command-line interface for Perplexity AI with beautiful terminal output and Obsidian note integration.

## Features

- **Conversational by default** - All queries are interactive with context preservation
- **Beautiful formatting** - Markdown rendering with syntax highlighting and clickable links
- **Research mode** - Deep analysis with the `sonar-reasoning` model
- **Claude Code integration** - Non-interactive mode with JSON/markdown output for programmatic use
- **Obsidian integration** - Save conversations as formatted markdown notes
- **Automatic citations** - Clickable source links in your terminal
- **Smart retry logic** - Handles rate limits and network errors gracefully

## Installation

```bash
npm install -g pp-cli
```

After installation, configure your API key and vault path:

```bash
pp config
```

You'll be prompted for:
- **Perplexity API Key** - Get one at [perplexity.ai](https://www.perplexity.ai/)
- **Obsidian Vault Path** - Path to your searches directory (e.g., `/Users/you/vault/searches`)
- **Default Model** - Press Enter for `sonar-pro`

## Usage

### Interactive Queries

Every query starts an interactive conversation. Ask your initial question, then follow up:

```bash
pp rust ownership
> how does it differ from garbage collection
> show me an example with a vector
> exit
Save to vault? (y/n): y
✓ Saved to: 2025-11-06-rust-ownership-basics.md
```

**Interactive features:**
- Each response maintains full conversation context
- Type `exit` or `quit` to end the session
- Always prompted to save the full conversation to Obsidian
- Responses stream with beautiful markdown formatting
- Citations displayed with clickable links

**Note about contractions:** Wrap queries with contractions in quotes:
```bash
pp "what's the difference between rust and c++"
```

### Deep Research Mode

Use the `-r` flag for comprehensive research with the `sonar-reasoning` model:

```bash
pp -r latest advances in quantum computing
> what are the main challenges
> which companies are leading
> exit
Save to vault? (y/n): y
✓ Saved to: 2025-11-06-quantum-computing-advances.md
```

Research mode provides:
- More detailed, comprehensive responses using advanced reasoning
- "Thinking deeply..." indicator during processing
- Better for in-depth analysis and complex topics
- Same interactive experience with context preservation

### Programmatic Usage (Claude Code Integration)

Use non-interactive mode for scripting and Claude Code integration:

```bash
# Get JSON output for parsing
pp --no-interactive "what is rust ownership" --output json

# Get raw markdown
pp --no-interactive "explain TypeScript generics" --output markdown

# Save to specific Obsidian note
pp --no-interactive "Node.js advantages" --save-to "dev/nodejs-notes.md"

# Append to existing note
pp --no-interactive "follow-up question" --append-to "dev/nodejs-notes.md"

# Research mode with JSON output
pp -r --no-interactive "quantum computing" --output json
```

**Non-interactive flags:**
- `--no-interactive` - Skips follow-up prompts (for scripting)
- `--output <format>` - Choose `text`, `json`, or `markdown`
- `--save-to <path>` - Save to specific note path (relative to vault)
- `--append-to <path>` - Append to existing note

**JSON output format:**
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

### Obsidian Notes

When you save a conversation, pp-cli creates a markdown note with:

- **YAML frontmatter** - Timestamp, original query, tags
- **Q&A format** - Clear question and answer structure
- **Full conversation** - Every question and response
- **Sources section** - All citations with clickable links

Example saved note:
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

## Terminal Features

- **Markdown Rendering** - Headers, lists, code blocks properly formatted
- **Syntax Highlighting** - Code blocks with language-specific colors
- **Clickable Links** - CMD+click URLs to open (in supported terminals like iTerm2)
- **Beautiful Citations** - Numbered sources with clickable links
- **Progress Indicators** - Visual feedback during processing

## Configuration

View or update your settings:

```bash
pp config
```

Config is stored at `~/.config/pp/config.json`

## Requirements

- **Node.js** >= 18
- **Perplexity API key** - Required for all searches
- **Obsidian vault** - Optional, only needed for saving notes

## Commands

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

## Examples

```bash
# Quick conversational query
pp capital of france
> what about the history
> exit

# Technical deep dive
pp rust memory management
> compare to c++ smart pointers
> show ownership examples
> exit
Save to vault? y

# Research mode for complex topics
pp -r "latest advances in fusion energy"
> what are the main challenges
> compare inertial vs magnetic confinement
> exit
Save to vault? y

# Non-interactive with JSON output (for Claude Code)
pp --no-interactive "explain async/await in JavaScript" --output json

# Save directly to specific note
pp --no-interactive "TypeScript best practices" --save-to "dev/typescript.md"

# Append follow-up to existing note
pp --no-interactive "advanced TypeScript patterns" --append-to "dev/typescript.md"
```

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
