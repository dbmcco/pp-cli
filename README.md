# pp-cli

Perplexity CLI search tool with interactive mode and Obsidian integration.

## Installation

```bash
npm install -g pp-cli
pp config  # Configure API key and vault path
```

## Usage

### Simple search
```bash
pp "what is rust ownership"
```

### Interactive mode
```bash
pp -i "what is rust ownership"
> why is this better than GC?
> exit
Save to vault? (y/n): y
```

### Configuration
```bash
pp config  # Reconfigure settings
```

## Requirements

- Node.js >= 18
- Perplexity API key
- Obsidian vault (optional)

## License

MIT
