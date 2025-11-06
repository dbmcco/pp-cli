# Perplexity CLI Tool Design

**Date:** 2025-11-06
**Project:** pp - Perplexity CLI search tool
**Location:** `/experiments/pp`

## Overview

A command-line tool for executing Perplexity searches with three primary modes:
1. Quick terminal searches with concise answers
2. Interactive conversation mode with context maintenance
3. Optional save to Obsidian vault with full conversation + sources

## Requirements

### User Requirements
- Zero-friction quick searches from terminal
- Interactive mode for follow-up questions with maintained context
- Save conversations to Obsidian with proper formatting and citations
- Simple installation and configuration
- Fast iteration based on user feedback

### Technical Requirements
- Single command: `pp`
- Config stored in `~/.config/pp/config.json`
- TypeScript/Node.js for fast development and iteration
- Global npm installation
- Clean error handling and user feedback

## CLI Interface

### Command Structure

```bash
pp "query"              # Quick search, terminal output only
pp -i "query"           # Interactive mode with save prompt on exit
pp -i -v "query"        # Mix flags as needed
```

### Flags

- `-i, --interactive` - Enter conversation mode with context maintenance
- No `-o` flag needed - save prompt happens on exit in interactive mode
- No `-v` flag in CLI - sources always included when saving to Obsidian

### Usage Flow

**Simple Mode:**
```
$ pp "what is rust ownership"
Rust's ownership system ensures memory safety without garbage collection...
[concise 3-5 sentence answer]
```

**Interactive Mode:**
```
$ pp -i "what is rust ownership"
Rust's ownership system ensures memory safety...

> why is this better than garbage collection
[response with context from first question]

> exit
Save to vault? (y/n): y
Generating filename... ✓
Saved to: searches/2025-11-06-rust-ownership-memory-safety.md
```

## Configuration Management

### Storage Location
`~/.config/pp/config.json`

### Configuration Structure
```json
{
  "apiKey": "pplx-...",
  "vaultPath": "/Users/braydon/obsidian/bvault/searches",
  "defaultModel": "sonar-pro"
}
```

### Setup Flow
- First run or `pp --config` triggers interactive prompts
- User pastes API key directly into CLI
- User provides vault path (validated)
- Config saved for future use
- Environment variable overrides: `PERPLEXITY_API_KEY`, `OBSIDIAN_VAULT_PATH`

## API Integration

### Perplexity API
- Endpoint: Chat completions API
- Model: `sonar-pro` (configurable)
- Conversation history maintained in interactive mode

### Request Structure
```typescript
{
  model: "sonar-pro",
  messages: [
    {role: "user", content: "query"},
    {role: "assistant", content: "response"},
    {role: "user", content: "follow-up"}
  ]
}
```

### Response Handling
- Extract content from API response
- Format for terminal display (concise)
- Maintain conversation array for interactive mode
- Extract sources/citations for Obsidian saves

### Error Handling
- Invalid API key → Point to config setup
- Rate limits → Clear message with wait time
- Network errors → 3 retry attempts with exponential backoff
- Invalid responses → Log and show friendly error

## Obsidian Integration

### File Naming
- Pattern: `YYYY-MM-DD-topic-slug.md`
- Slug generation: Separate API call to Perplexity
  - Prompt: "Summarize this conversation topic in 3-5 words"
  - Slugify result (lowercase, dashes, word boundaries)
- Collision handling: Append `-2`, `-3` etc

### File Format
```markdown
---
created: 2025-11-06T14:32:00
query: "Original query text"
tags: [perplexity, search]
---

# Topic Title (from slug generation)

**Q:** Your original query
**A:** Perplexity's response...

---

**Q:** Follow-up question
**A:** Follow-up response...

---

## Sources
- [Source 1 title](url)
- [Source 2 title](url)
- [Source 3 title](url)
```

### Save Behavior
- Terminal output never shows sources (stays clean)
- Obsidian saves always include sources section
- Full conversation thread saved
- Q&A format for clarity

## Technical Architecture

### Technology Stack
- **Runtime:** Node.js with TypeScript
- **CLI:** Commander.js
- **HTTP:** Axios
- **UI:** ora (spinners), chalk (colors), inquirer (prompts)
- **Installation:** npm global install

### Project Structure
```
pp-cli/
├── src/
│   ├── index.ts          # CLI entry point, command routing
│   ├── commands/
│   │   ├── search.ts     # Simple search handler
│   │   ├── interactive.ts # Interactive mode handler
│   │   └── config.ts     # Config setup command
│   ├── api/
│   │   └── perplexity.ts # API client, request/response handling
│   ├── config/
│   │   └── manager.ts    # Config read/write/validation
│   ├── obsidian/
│   │   ├── writer.ts     # File creation, formatting
│   │   └── slugify.ts    # Topic slug generation
│   └── utils/
│       ├── formatter.ts  # Terminal output formatting
│       └── errors.ts     # Error handling utilities
├── package.json
├── tsconfig.json
└── README.md
```

### Key Components

#### API Client (`api/perplexity.ts`)
- Handles all Perplexity API communication
- Maintains conversation history
- Implements retry logic
- Extracts and formats responses

#### Interactive Handler (`commands/interactive.ts`)
- Manages conversation loop
- Maintains message history array
- Handles exit command
- Triggers save prompt

#### Obsidian Writer (`obsidian/writer.ts`)
- Generates topic slug via API
- Creates properly formatted markdown
- Handles file collisions
- Validates vault path

#### Config Manager (`config/manager.ts`)
- Reads/writes `~/.config/pp/config.json`
- Interactive setup prompts
- Environment variable support
- Path validation

## User Experience

### Terminal Output
- Spinners during API calls
- Success indicators: `✓`
- Colored output for readability
- Clear error messages in red
- Clean, concise responses

### Interactive Mode
- Prompt: `>` for user input
- Commands: `exit`, `quit`, `Ctrl+C`
- Save prompt only on normal exit (not Ctrl+C)
- Context maintained throughout session

### Error Messages
- "Invalid API key. Run `pp --config` to update."
- "Rate limit hit. Try again in 30 seconds."
- "Vault path not found: /path/to/vault"
- "Failed to connect to Perplexity API. Retrying..."

## Edge Cases

### Configuration
- Missing config → Interactive setup
- Invalid vault path → Offer to create directory
- Invalid API key → Clear error with setup instructions

### API Issues
- Rate limiting → Show wait time, don't retry automatically
- Network timeout → 3 retries, exponential backoff
- Invalid response format → Log raw response, show error

### File System
- Vault directory doesn't exist → Ask to create
- Filename collision → Append counter
- No write permissions → Clear error message

### Interactive Mode
- Empty input → Re-prompt
- Very long conversations → All saved correctly
- Ctrl+C → Immediate exit, no save prompt

## Installation & Distribution

### Installation
```bash
npm install -g pp-cli
pp --config
pp "test query"
```

### Updates
```bash
npm update -g pp-cli
```

### Development Workflow
1. Build tool with TypeScript
2. Provide compiled executable to Braydon
3. User testing and directional feedback
4. Iterate on feedback
5. Push updates to npm for easy installation

## Success Criteria

- Installation takes < 2 minutes (including config)
- Quick searches return in < 3 seconds
- Interactive mode feels responsive
- Obsidian files are well-formatted and useful
- Error messages are helpful, not cryptic
- Zero maintenance required after setup

## Future Considerations

- Potential Rust rewrite if tool reaches stable v1.0
- Different Perplexity models (research, deep-dive)
- Custom frontmatter fields for Obsidian
- Search history/cache
- Output format templates
