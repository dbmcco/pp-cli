# pp-cli

A command-line interface for Perplexity AI with interactive conversations and Obsidian note integration.

## Features

- **Simple searches** - Get instant answers from the command line
- **Interactive mode** - Have multi-turn conversations with context preservation
- **Obsidian integration** - Save conversations as formatted markdown notes
- **Automatic citations** - Sources included when saving to vault
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

### Simple Search

Get a quick answer without conversation history:

```bash
pp what is rust ownership
```

### Interactive Mode

Have a conversation with follow-up questions:

```bash
pp -i explain quantum computing
> how does it differ from classical computing
> what are practical applications
> exit
Save to vault? (y/n): y
✓ Saved to: 2025-11-06-quantum-computing-basics.md
```

In interactive mode:
- Each response maintains conversation context
- Type `exit` or `quit` to end the session
- Choose whether to save the full conversation to Obsidian

### Deep Research Mode

Use the `-r` flag for comprehensive research with the `sonar-reasoning` model:

```bash
pp -i -r latest advances in quantum computing
> what are the main challenges
> which companies are leading
> exit
Save to vault? (y/n): y
✓ Saved to: 2025-11-06-quantum-computing-advances.md
```

Research mode provides:
- More detailed, comprehensive responses using advanced reasoning
- Better for in-depth analysis and complex topics
- Ideal for research that you want to save and reference later

### Obsidian Notes

When you save a conversation, pp-cli creates a markdown note with:

- **YAML frontmatter** - Timestamp, original query, tags
- **Q&A format** - Clear question and answer structure
- **Full conversation** - Every question and response
- **Sources section** - Citations with links

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
pp [query...]              Run a simple search
pp -i [query...]           Start interactive mode
pp -r [query...]           Deep research mode with comprehensive analysis
pp -i -r [query...]        Interactive research mode
pp config                  Configure API key and vault path
pp --version               Show version
pp --help                  Show help
```

## Examples

```bash
# Quick facts
pp capital of france

# Technical explanations
pp -i how does rust handle memory

# Research with sources
pp -i latest advances in fusion energy
> what are the main challenges
> exit
Save to vault? y
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
