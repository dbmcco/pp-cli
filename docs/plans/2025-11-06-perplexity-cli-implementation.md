# Perplexity CLI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a TypeScript CLI tool for executing Perplexity searches with interactive mode and Obsidian integration.

**Architecture:** Commander.js CLI → API client → Formatter → Obsidian writer. Config stored in ~/.config/pp/config.json. Tests use vitest with no mocks.

**Tech Stack:** TypeScript, Node.js, Commander.js, Axios, Inquirer, Chalk, Ora

---

## Task 1: Project Initialization

**Files:**
- Create: `package.json`
- Create: `tsconfig.json`
- Create: `.gitignore`
- Create: `src/index.ts`

**Step 1: Create package.json**

```bash
cd /Users/braydon/projects/experiments/pp
```

Create `package.json`:
```json
{
  "name": "pp-cli",
  "version": "0.1.0",
  "description": "Perplexity CLI search tool",
  "main": "dist/index.js",
  "bin": {
    "pp": "./dist/index.js"
  },
  "scripts": {
    "build": "tsc",
    "dev": "tsx src/index.ts",
    "test": "vitest",
    "test:watch": "vitest --watch",
    "lint": "eslint src --ext .ts",
    "type-check": "tsc --noEmit"
  },
  "keywords": ["cli", "perplexity", "search"],
  "author": "Braydon",
  "license": "MIT",
  "dependencies": {
    "commander": "^11.1.0",
    "axios": "^1.6.2",
    "inquirer": "^9.2.12",
    "chalk": "^5.3.0",
    "ora": "^8.0.1"
  },
  "devDependencies": {
    "@types/node": "^20.10.5",
    "@types/inquirer": "^9.0.7",
    "typescript": "^5.3.3",
    "tsx": "^4.7.0",
    "vitest": "^1.1.0",
    "eslint": "^8.56.0",
    "@typescript-eslint/parser": "^6.16.0",
    "@typescript-eslint/eslint-plugin": "^6.16.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

**Step 2: Create tsconfig.json**

Create `tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "moduleResolution": "node"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
```

**Step 3: Create .gitignore**

Create `.gitignore`:
```
node_modules/
dist/
*.log
.DS_Store
.env
```

**Step 4: Create minimal index.ts**

Create `src/index.ts`:
```typescript
#!/usr/bin/env node
// ABOUTME: CLI entry point for pp-cli

console.log('pp-cli v0.1.0');
```

**Step 5: Install dependencies**

Run: `npm install`
Expected: All dependencies installed successfully

**Step 6: Test build**

Run: `npm run build`
Expected: `dist/index.js` created successfully

**Step 7: Commit**

```bash
git add package.json tsconfig.json .gitignore src/index.ts
git commit -m "feat: initialize TypeScript project structure"
```

---

## Task 2: Config Manager - Read Config

**Files:**
- Create: `src/config/types.ts`
- Create: `src/config/manager.ts`
- Create: `src/config/manager.test.ts`

**Step 1: Write types definition**

Create `src/config/types.ts`:
```typescript
// ABOUTME: Type definitions for configuration

export interface Config {
  apiKey: string;
  vaultPath: string;
  defaultModel: string;
}

export const DEFAULT_CONFIG_DIR = '.config/pp';
export const CONFIG_FILENAME = 'config.json';
```

**Step 2: Write failing test for config reading**

Create `src/config/manager.test.ts`:
```typescript
// ABOUTME: Tests for configuration management

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { promises as fs } from 'fs';
import * as path from 'path';
import * as os from 'os';
import { ConfigManager } from './manager';

describe('ConfigManager', () => {
  let testConfigDir: string;
  let configManager: ConfigManager;

  beforeEach(async () => {
    // Create temp config directory
    testConfigDir = path.join(os.tmpdir(), `pp-test-${Date.now()}`);
    await fs.mkdir(testConfigDir, { recursive: true });
    configManager = new ConfigManager(testConfigDir);
  });

  afterEach(async () => {
    // Clean up
    await fs.rm(testConfigDir, { recursive: true, force: true });
  });

  describe('readConfig', () => {
    it('should return null when config file does not exist', async () => {
      const config = await configManager.readConfig();
      expect(config).toBeNull();
    });

    it('should read and parse existing config file', async () => {
      const expectedConfig = {
        apiKey: 'test-key',
        vaultPath: '/test/path',
        defaultModel: 'sonar-pro'
      };

      const configPath = path.join(testConfigDir, 'config.json');
      await fs.writeFile(configPath, JSON.stringify(expectedConfig));

      const config = await configManager.readConfig();
      expect(config).toEqual(expectedConfig);
    });
  });
});
```

**Step 3: Run test to verify it fails**

Run: `npm test`
Expected: FAIL with "Cannot find module './manager'"

**Step 4: Write minimal implementation**

Create `src/config/manager.ts`:
```typescript
// ABOUTME: Configuration file management

import { promises as fs } from 'fs';
import * as path from 'path';
import * as os from 'os';
import { Config, DEFAULT_CONFIG_DIR, CONFIG_FILENAME } from './types';

export class ConfigManager {
  private configDir: string;
  private configPath: string;

  constructor(configDir?: string) {
    this.configDir = configDir || path.join(os.homedir(), DEFAULT_CONFIG_DIR);
    this.configPath = path.join(this.configDir, CONFIG_FILENAME);
  }

  async readConfig(): Promise<Config | null> {
    try {
      const data = await fs.readFile(this.configPath, 'utf-8');
      return JSON.parse(data) as Config;
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        return null;
      }
      throw error;
    }
  }
}
```

**Step 5: Run test to verify it passes**

Run: `npm test`
Expected: All tests PASS

**Step 6: Commit**

```bash
git add src/config/
git commit -m "feat: add config reading functionality"
```

---

## Task 3: Config Manager - Write Config

**Files:**
- Modify: `src/config/manager.ts`
- Modify: `src/config/manager.test.ts`

**Step 1: Write failing test for config writing**

Add to `src/config/manager.test.ts` inside the `describe('ConfigManager')` block:

```typescript
  describe('writeConfig', () => {
    it('should create config directory if it does not exist', async () => {
      await fs.rm(testConfigDir, { recursive: true, force: true });

      const config = {
        apiKey: 'test-key',
        vaultPath: '/test/path',
        defaultModel: 'sonar-pro'
      };

      await configManager.writeConfig(config);

      const exists = await fs.access(testConfigDir).then(() => true).catch(() => false);
      expect(exists).toBe(true);
    });

    it('should write config to file', async () => {
      const config = {
        apiKey: 'test-key',
        vaultPath: '/test/path',
        defaultModel: 'sonar-pro'
      };

      await configManager.writeConfig(config);

      const configPath = path.join(testConfigDir, 'config.json');
      const data = await fs.readFile(configPath, 'utf-8');
      expect(JSON.parse(data)).toEqual(config);
    });
  });
```

**Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL with "writeConfig is not a function"

**Step 3: Write minimal implementation**

Add to `src/config/manager.ts`:

```typescript
  async writeConfig(config: Config): Promise<void> {
    await fs.mkdir(this.configDir, { recursive: true });
    await fs.writeFile(this.configPath, JSON.stringify(config, null, 2));
  }
```

**Step 4: Run test to verify it passes**

Run: `npm test`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/config/manager.ts src/config/manager.test.ts
git commit -m "feat: add config writing functionality"
```

---

## Task 4: Config Manager - Interactive Setup

**Files:**
- Modify: `src/config/manager.ts`
- Create: `src/config/prompts.ts`

**Step 1: Create prompts module**

Create `src/config/prompts.ts`:
```typescript
// ABOUTME: Interactive prompts for configuration setup

import inquirer from 'inquirer';
import { Config } from './types';

export async function promptForConfig(): Promise<Config> {
  const answers = await inquirer.prompt([
    {
      type: 'password',
      name: 'apiKey',
      message: 'Perplexity API Key:',
      validate: (input: string) => {
        if (!input || input.trim().length === 0) {
          return 'API key is required';
        }
        return true;
      }
    },
    {
      type: 'input',
      name: 'vaultPath',
      message: 'Obsidian Vault Path:',
      validate: (input: string) => {
        if (!input || input.trim().length === 0) {
          return 'Vault path is required';
        }
        return true;
      }
    },
    {
      type: 'input',
      name: 'defaultModel',
      message: 'Default Perplexity Model:',
      default: 'sonar-pro'
    }
  ]);

  return answers as Config;
}
```

**Step 2: Add setupConfig method**

Add to `src/config/manager.ts`:

```typescript
import { promptForConfig } from './prompts';

  async setupConfig(): Promise<Config> {
    const config = await promptForConfig();
    await this.writeConfig(config);
    return config;
  }

  async getOrSetupConfig(): Promise<Config> {
    const existing = await this.readConfig();
    if (existing) {
      return existing;
    }
    return this.setupConfig();
  }
```

**Step 3: Test manually**

Run: `npm run dev` (will run index.ts)
Expected: Builds successfully (we'll test interactive setup in later task)

**Step 4: Commit**

```bash
git add src/config/prompts.ts src/config/manager.ts
git commit -m "feat: add interactive config setup"
```

---

## Task 5: Perplexity API Client - Types and Structure

**Files:**
- Create: `src/api/types.ts`
- Create: `src/api/client.ts`
- Create: `src/api/client.test.ts`

**Step 1: Create API types**

Create `src/api/types.ts`:
```typescript
// ABOUTME: Type definitions for Perplexity API

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface PerplexityRequest {
  model: string;
  messages: Message[];
}

export interface Citation {
  title: string;
  url: string;
}

export interface PerplexityResponse {
  id: string;
  model: string;
  created: number;
  choices: Array<{
    index: number;
    message: Message;
    finish_reason: string;
  }>;
  citations?: Citation[];
}
```

**Step 2: Write failing test for API client initialization**

Create `src/api/client.test.ts`:
```typescript
// ABOUTME: Tests for Perplexity API client

import { describe, it, expect } from 'vitest';
import { PerplexityClient } from './client';

describe('PerplexityClient', () => {
  it('should initialize with API key and model', () => {
    const client = new PerplexityClient('test-key', 'sonar-pro');
    expect(client).toBeDefined();
  });
});
```

**Step 3: Run test to verify it fails**

Run: `npm test`
Expected: FAIL with "Cannot find module './client'"

**Step 4: Write minimal implementation**

Create `src/api/client.ts`:
```typescript
// ABOUTME: Perplexity API client

import axios, { AxiosInstance } from 'axios';
import { PerplexityRequest, PerplexityResponse, Message } from './types';

export class PerplexityClient {
  private apiKey: string;
  private model: string;
  private client: AxiosInstance;

  constructor(apiKey: string, model: string = 'sonar-pro') {
    this.apiKey = apiKey;
    this.model = model;
    this.client = axios.create({
      baseURL: 'https://api.perplexity.ai',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      }
    });
  }
}
```

**Step 5: Run test to verify it passes**

Run: `npm test`
Expected: All tests PASS

**Step 6: Commit**

```bash
git add src/api/
git commit -m "feat: add Perplexity API client structure"
```

---

## Task 6: Perplexity API Client - Send Query

**Files:**
- Modify: `src/api/client.ts`
- Modify: `src/api/client.test.ts`

**Step 1: Write failing test for query**

Add to `src/api/client.test.ts`:

```typescript
import { vi, describe, it, expect, beforeEach } from 'vitest';
import axios from 'axios';

vi.mock('axios');
const mockedAxios = axios as any;

describe('PerplexityClient', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ... existing test ...

  describe('query', () => {
    it('should send query and return response', async () => {
      const mockResponse = {
        data: {
          id: 'test-id',
          model: 'sonar-pro',
          created: 123456,
          choices: [{
            index: 0,
            message: {
              role: 'assistant',
              content: 'Test response'
            },
            finish_reason: 'stop'
          }],
          citations: [
            { title: 'Test Source', url: 'https://example.com' }
          ]
        }
      };

      mockedAxios.create.mockReturnValue({
        post: vi.fn().mockResolvedValue(mockResponse)
      });

      const client = new PerplexityClient('test-key', 'sonar-pro');
      const result = await client.query('test query');

      expect(result.content).toBe('Test response');
      expect(result.citations).toHaveLength(1);
      expect(result.citations[0].title).toBe('Test Source');
    });
  });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL with "query is not a function"

**Step 3: Write minimal implementation**

Add to `src/api/client.ts`:

```typescript
import { Citation } from './types';

export interface QueryResult {
  content: string;
  citations: Citation[];
}

export class PerplexityClient {
  // ... existing code ...

  async query(userQuery: string, conversationHistory: Message[] = []): Promise<QueryResult> {
    const messages: Message[] = [
      ...conversationHistory,
      { role: 'user', content: userQuery }
    ];

    const request: PerplexityRequest = {
      model: this.model,
      messages
    };

    const response = await this.client.post<PerplexityResponse>('/chat/completions', request);

    return {
      content: response.data.choices[0].message.content,
      citations: response.data.citations || []
    };
  }
}
```

**Step 4: Run test to verify it passes**

Run: `npm test`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/api/client.ts src/api/client.test.ts
git commit -m "feat: add query method to API client"
```

---

## Task 7: Slugify Utility

**Files:**
- Create: `src/utils/slugify.ts`
- Create: `src/utils/slugify.test.ts`

**Step 1: Write failing test for slugify**

Create `src/utils/slugify.test.ts`:
```typescript
// ABOUTME: Tests for slug generation

import { describe, it, expect } from 'vitest';
import { slugify } from './slugify';

describe('slugify', () => {
  it('should convert text to lowercase slug', () => {
    expect(slugify('What Is Rust Ownership')).toBe('what-is-rust-ownership');
  });

  it('should replace spaces with dashes', () => {
    expect(slugify('hello world test')).toBe('hello-world-test');
  });

  it('should remove special characters', () => {
    expect(slugify('test? & example!')).toBe('test-example');
  });

  it('should truncate at word boundaries', () => {
    const longText = 'this is a very long text that should be truncated at a reasonable word boundary';
    const result = slugify(longText, 30);
    expect(result.length).toBeLessThanOrEqual(35); // Allow some buffer for word boundary
    expect(result).not.toContain(' ');
    expect(result.endsWith('-')).toBe(false);
  });

  it('should handle multiple consecutive spaces', () => {
    expect(slugify('hello    world')).toBe('hello-world');
  });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL with "Cannot find module './slugify'"

**Step 3: Write minimal implementation**

Create `src/utils/slugify.ts`:
```typescript
// ABOUTME: Slug generation utility

export function slugify(text: string, maxLength: number = 50): string {
  // Convert to lowercase and replace spaces with dashes
  let slug = text
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9-]/g, '');

  // Remove consecutive dashes
  slug = slug.replace(/-+/g, '-');

  // Truncate at word boundary
  if (slug.length > maxLength) {
    slug = slug.substring(0, maxLength);
    const lastDash = slug.lastIndexOf('-');
    if (lastDash > maxLength * 0.6) {
      slug = slug.substring(0, lastDash);
    }
  }

  // Remove trailing dash
  slug = slug.replace(/-$/, '');

  return slug;
}
```

**Step 4: Run test to verify it passes**

Run: `npm test`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/utils/slugify.ts src/utils/slugify.test.ts
git commit -m "feat: add slugify utility"
```

---

## Task 8: Obsidian Writer - Markdown Formatting

**Files:**
- Create: `src/obsidian/types.ts`
- Create: `src/obsidian/formatter.ts`
- Create: `src/obsidian/formatter.test.ts`

**Step 1: Create types**

Create `src/obsidian/types.ts`:
```typescript
// ABOUTME: Types for Obsidian integration

import { Citation } from '../api/types';

export interface ConversationEntry {
  question: string;
  answer: string;
}

export interface ObsidianNote {
  title: string;
  query: string;
  conversation: ConversationEntry[];
  citations: Citation[];
}
```

**Step 2: Write failing test for markdown formatting**

Create `src/obsidian/formatter.test.ts`:
```typescript
// ABOUTME: Tests for Obsidian markdown formatting

import { describe, it, expect } from 'vitest';
import { formatAsMarkdown } from './formatter';
import { ObsidianNote } from './types';

describe('formatAsMarkdown', () => {
  it('should format note with frontmatter and content', () => {
    const note: ObsidianNote = {
      title: 'Rust Ownership',
      query: 'What is Rust ownership?',
      conversation: [
        {
          question: 'What is Rust ownership?',
          answer: 'Rust ownership is a memory safety system.'
        }
      ],
      citations: [
        { title: 'Rust Docs', url: 'https://doc.rust-lang.org' }
      ]
    };

    const markdown = formatAsMarkdown(note);

    expect(markdown).toContain('---');
    expect(markdown).toContain('query: "What is Rust ownership?"');
    expect(markdown).toContain('tags: [perplexity, search]');
    expect(markdown).toContain('# Rust Ownership');
    expect(markdown).toContain('**Q:** What is Rust ownership?');
    expect(markdown).toContain('**A:** Rust ownership is a memory safety system.');
    expect(markdown).toContain('## Sources');
    expect(markdown).toContain('- [Rust Docs](https://doc.rust-lang.org)');
  });

  it('should format multiple conversation entries', () => {
    const note: ObsidianNote = {
      title: 'Test Topic',
      query: 'Initial query',
      conversation: [
        { question: 'Question 1', answer: 'Answer 1' },
        { question: 'Question 2', answer: 'Answer 2' }
      ],
      citations: []
    };

    const markdown = formatAsMarkdown(note);

    expect(markdown).toContain('**Q:** Question 1');
    expect(markdown).toContain('**A:** Answer 1');
    expect(markdown).toContain('---');
    expect(markdown).toContain('**Q:** Question 2');
    expect(markdown).toContain('**A:** Answer 2');
  });
});
```

**Step 3: Run test to verify it fails**

Run: `npm test`
Expected: FAIL with "Cannot find module './formatter'"

**Step 4: Write minimal implementation**

Create `src/obsidian/formatter.ts`:
```typescript
// ABOUTME: Markdown formatting for Obsidian notes

import { ObsidianNote } from './types';

export function formatAsMarkdown(note: ObsidianNote): string {
  const now = new Date().toISOString();

  const parts: string[] = [];

  // Frontmatter
  parts.push('---');
  parts.push(`created: ${now}`);
  parts.push(`query: "${note.query}"`);
  parts.push('tags: [perplexity, search]');
  parts.push('---');
  parts.push('');

  // Title
  parts.push(`# ${note.title}`);
  parts.push('');

  // Conversation
  note.conversation.forEach((entry, index) => {
    if (index > 0) {
      parts.push('---');
      parts.push('');
    }
    parts.push(`**Q:** ${entry.question}`);
    parts.push(`**A:** ${entry.answer}`);
    parts.push('');
  });

  // Citations
  if (note.citations.length > 0) {
    parts.push('---');
    parts.push('');
    parts.push('## Sources');
    note.citations.forEach(citation => {
      parts.push(`- [${citation.title}](${citation.url})`);
    });
  }

  return parts.join('\n');
}
```

**Step 5: Run test to verify it passes**

Run: `npm test`
Expected: All tests PASS

**Step 6: Commit**

```bash
git add src/obsidian/
git commit -m "feat: add Obsidian markdown formatter"
```

---

## Task 9: Obsidian Writer - File Operations

**Files:**
- Create: `src/obsidian/writer.ts`
- Create: `src/obsidian/writer.test.ts`

**Step 1: Write failing test for file writing**

Create `src/obsidian/writer.test.ts`:
```typescript
// ABOUTME: Tests for Obsidian file writing

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { promises as fs } from 'fs';
import * as path from 'path';
import * as os from 'os';
import { ObsidianWriter } from './writer';
import { ObsidianNote } from './types';

describe('ObsidianWriter', () => {
  let testDir: string;
  let writer: ObsidianWriter;

  beforeEach(async () => {
    testDir = path.join(os.tmpdir(), `pp-obsidian-test-${Date.now()}`);
    await fs.mkdir(testDir, { recursive: true });
    writer = new ObsidianWriter(testDir);
  });

  afterEach(async () => {
    await fs.rm(testDir, { recursive: true, force: true });
  });

  describe('writeNote', () => {
    it('should write note to file with correct filename', async () => {
      const note: ObsidianNote = {
        title: 'Test Topic',
        query: 'test query',
        conversation: [
          { question: 'test query', answer: 'test answer' }
        ],
        citations: []
      };

      const filename = await writer.writeNote(note, 'test-topic');

      expect(filename).toMatch(/^\d{4}-\d{2}-\d{2}-test-topic\.md$/);

      const filepath = path.join(testDir, filename);
      const exists = await fs.access(filepath).then(() => true).catch(() => false);
      expect(exists).toBe(true);
    });

    it('should handle filename collisions', async () => {
      const note: ObsidianNote = {
        title: 'Test Topic',
        query: 'test query',
        conversation: [
          { question: 'test query', answer: 'test answer' }
        ],
        citations: []
      };

      const filename1 = await writer.writeNote(note, 'test-topic');
      const filename2 = await writer.writeNote(note, 'test-topic');

      expect(filename1).not.toBe(filename2);
      expect(filename2).toMatch(/-2\.md$/);
    });
  });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL with "Cannot find module './writer'"

**Step 3: Write minimal implementation**

Create `src/obsidian/writer.ts`:
```typescript
// ABOUTME: Obsidian file writer

import { promises as fs } from 'fs';
import * as path from 'path';
import { ObsidianNote } from './types';
import { formatAsMarkdown } from './formatter';

export class ObsidianWriter {
  private vaultPath: string;

  constructor(vaultPath: string) {
    this.vaultPath = vaultPath;
  }

  async writeNote(note: ObsidianNote, slug: string): Promise<string> {
    // Generate filename with date
    const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    let filename = `${date}-${slug}.md`;
    let filepath = path.join(this.vaultPath, filename);

    // Handle collisions
    let counter = 2;
    while (await this.fileExists(filepath)) {
      filename = `${date}-${slug}-${counter}.md`;
      filepath = path.join(this.vaultPath, filename);
      counter++;
    }

    // Write file
    const content = formatAsMarkdown(note);
    await fs.mkdir(this.vaultPath, { recursive: true });
    await fs.writeFile(filepath, content, 'utf-8');

    return filename;
  }

  private async fileExists(filepath: string): Promise<boolean> {
    try {
      await fs.access(filepath);
      return true;
    } catch {
      return false;
    }
  }
}
```

**Step 4: Run test to verify it passes**

Run: `npm test`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/obsidian/writer.ts src/obsidian/writer.test.ts
git commit -m "feat: add Obsidian file writer"
```

---

## Task 10: Simple Search Command

**Files:**
- Create: `src/commands/search.ts`
- Create: `src/commands/search.test.ts`

**Step 1: Write failing test for simple search**

Create `src/commands/search.test.ts`:
```typescript
// ABOUTME: Tests for simple search command

import { describe, it, expect, vi } from 'vitest';
import { simpleSearch } from './search';
import { PerplexityClient } from '../api/client';

vi.mock('../api/client');

describe('simpleSearch', () => {
  it('should query API and return formatted response', async () => {
    const mockQuery = vi.fn().mockResolvedValue({
      content: 'Test response',
      citations: []
    });

    const mockClient = {
      query: mockQuery
    } as unknown as PerplexityClient;

    const result = await simpleSearch(mockClient, 'test query');

    expect(mockQuery).toHaveBeenCalledWith('test query', []);
    expect(result).toBe('Test response');
  });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL with "Cannot find module './search'"

**Step 3: Write minimal implementation**

Create `src/commands/search.ts`:
```typescript
// ABOUTME: Simple search command handler

import { PerplexityClient } from '../api/client';

export async function simpleSearch(
  client: PerplexityClient,
  query: string
): Promise<string> {
  const result = await client.query(query);
  return result.content;
}
```

**Step 4: Run test to verify it passes**

Run: `npm test`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/commands/search.ts src/commands/search.test.ts
git commit -m "feat: add simple search command"
```

---

## Task 11: Interactive Mode Command

**Files:**
- Create: `src/commands/interactive.ts`
- Create: `src/commands/interactive.test.ts`

**Step 1: Write types and structure**

Create `src/commands/interactive.ts`:
```typescript
// ABOUTME: Interactive mode command handler

import inquirer from 'inquirer';
import { PerplexityClient } from '../api/client';
import { Message } from '../api/types';
import { ObsidianWriter } from '../obsidian/writer';
import { ObsidianNote, ConversationEntry } from '../obsidian/types';
import { Citation } from '../api/types';

export interface InteractiveSession {
  conversationHistory: Message[];
  conversationEntries: ConversationEntry[];
  allCitations: Citation[];
}

export async function startInteractiveSession(
  client: PerplexityClient,
  initialQuery: string,
  onResponse: (content: string) => void
): Promise<InteractiveSession> {
  const session: InteractiveSession = {
    conversationHistory: [],
    conversationEntries: [],
    allCitations: []
  };

  // Handle initial query
  await handleQuery(client, initialQuery, session, onResponse);

  // Interactive loop
  while (true) {
    const { input } = await inquirer.prompt([
      {
        type: 'input',
        name: 'input',
        message: '>',
        prefix: ''
      }
    ]);

    const trimmed = input.trim().toLowerCase();
    if (trimmed === 'exit' || trimmed === 'quit') {
      break;
    }

    if (input.trim()) {
      await handleQuery(client, input, session, onResponse);
    }
  }

  return session;
}

async function handleQuery(
  client: PerplexityClient,
  query: string,
  session: InteractiveSession,
  onResponse: (content: string) => void
): Promise<void> {
  const result = await client.query(query, session.conversationHistory);

  session.conversationHistory.push(
    { role: 'user', content: query },
    { role: 'assistant', content: result.content }
  );

  session.conversationEntries.push({
    question: query,
    answer: result.content
  });

  session.allCitations.push(...result.citations);

  onResponse(result.content);
}

export async function promptToSave(
  session: InteractiveSession,
  client: PerplexityClient,
  writer: ObsidianWriter,
  originalQuery: string
): Promise<string | null> {
  const { shouldSave } = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'shouldSave',
      message: 'Save to vault?',
      default: true
    }
  ]);

  if (!shouldSave) {
    return null;
  }

  // Generate topic slug
  const slugPrompt = `Summarize this conversation topic in 3-5 words: "${originalQuery}"`;
  const slugResult = await client.query(slugPrompt);
  const slug = slugResult.content.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

  // Create note
  const note: ObsidianNote = {
    title: slugResult.content,
    query: originalQuery,
    conversation: session.conversationEntries,
    citations: session.allCitations
  };

  const filename = await writer.writeNote(note, slug);
  return filename;
}
```

**Step 2: Test build**

Run: `npm run build`
Expected: Builds successfully

**Step 3: Commit**

```bash
git add src/commands/interactive.ts
git commit -m "feat: add interactive mode command"
```

---

## Task 12: CLI Entry Point

**Files:**
- Modify: `src/index.ts`
- Create: `src/cli.ts`

**Step 1: Create CLI handler**

Create `src/cli.ts`:
```typescript
// ABOUTME: CLI command handling

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { ConfigManager } from './config/manager';
import { PerplexityClient } from './api/client';
import { ObsidianWriter } from './obsidian/writer';
import { simpleSearch } from './commands/search';
import { startInteractiveSession, promptToSave } from './commands/interactive';

export async function runCLI() {
  const program = new Command();

  program
    .name('pp')
    .description('Perplexity CLI search tool')
    .version('0.1.0');

  program
    .argument('<query>', 'search query')
    .option('-i, --interactive', 'interactive mode with conversation')
    .action(async (query: string, options: { interactive?: boolean }) => {
      try {
        // Load config
        const configManager = new ConfigManager();
        const config = await configManager.getOrSetupConfig();

        // Initialize client and writer
        const client = new PerplexityClient(config.apiKey, config.defaultModel);
        const writer = new ObsidianWriter(config.vaultPath);

        if (options.interactive) {
          // Interactive mode
          const session = await startInteractiveSession(
            client,
            query,
            (content) => {
              console.log(chalk.cyan(content));
              console.log();
            }
          );

          const filename = await promptToSave(session, client, writer, query);
          if (filename) {
            console.log(chalk.green(`✓ Saved to: ${filename}`));
          }
        } else {
          // Simple search
          const spinner = ora('Searching...').start();
          const result = await simpleSearch(client, query);
          spinner.stop();
          console.log(result);
        }
      } catch (error) {
        console.error(chalk.red('Error:'), (error as Error).message);
        process.exit(1);
      }
    });

  program
    .command('config')
    .description('Configure pp-cli')
    .action(async () => {
      try {
        const configManager = new ConfigManager();
        const config = await configManager.setupConfig();
        console.log(chalk.green('✓ Configuration saved'));
        console.log('API Key:', config.apiKey.substring(0, 10) + '...');
        console.log('Vault Path:', config.vaultPath);
        console.log('Model:', config.defaultModel);
      } catch (error) {
        console.error(chalk.red('Error:'), (error as Error).message);
        process.exit(1);
      }
    });

  await program.parseAsync(process.argv);
}
```

**Step 2: Update index.ts**

Replace `src/index.ts` with:
```typescript
#!/usr/bin/env node
// ABOUTME: CLI entry point for pp-cli

import { runCLI } from './cli';

runCLI().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
```

**Step 3: Build and test locally**

Run: `npm run build`
Expected: Builds successfully

Run: `chmod +x dist/index.js`
Expected: Makes executable

Run: `node dist/index.js --help`
Expected: Shows help text

**Step 4: Commit**

```bash
git add src/index.ts src/cli.ts
git commit -m "feat: implement CLI entry point"
```

---

## Task 13: Error Handling and Retry Logic

**Files:**
- Modify: `src/api/client.ts`

**Step 1: Add retry logic with exponential backoff**

Add to `src/api/client.ts`:

```typescript
  private async retryWithBackoff<T>(
    fn: () => Promise<T>,
    maxRetries: number = 3
  ): Promise<T> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;

        // Don't retry on auth errors
        if (axios.isAxiosError(error) && error.response?.status === 401) {
          throw new Error('Invalid API key. Run `pp config` to update.');
        }

        // Don't retry on rate limit errors
        if (axios.isAxiosError(error) && error.response?.status === 429) {
          const retryAfter = error.response.headers['retry-after'] || '60';
          throw new Error(`Rate limit hit. Try again in ${retryAfter} seconds.`);
        }

        // Wait before retrying
        if (attempt < maxRetries - 1) {
          const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    throw lastError || new Error('Request failed');
  }

  async query(userQuery: string, conversationHistory: Message[] = []): Promise<QueryResult> {
    return this.retryWithBackoff(async () => {
      const messages: Message[] = [
        ...conversationHistory,
        { role: 'user', content: userQuery }
      ];

      const request: PerplexityRequest = {
        model: this.model,
        messages
      };

      const response = await this.client.post<PerplexityResponse>('/chat/completions', request);

      return {
        content: response.data.choices[0].message.content,
        citations: response.data.citations || []
      };
    });
  }
```

**Step 2: Test build**

Run: `npm run build`
Expected: Builds successfully

**Step 3: Commit**

```bash
git add src/api/client.ts
git commit -m "feat: add retry logic with exponential backoff"
```

---

## Task 14: Package Preparation

**Files:**
- Create: `README.md`
- Create: `.npmignore`

**Step 1: Create README**

Create `README.md`:
```markdown
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
```

**Step 2: Create .npmignore**

Create `.npmignore`:
```
src/
*.test.ts
vitest.config.ts
tsconfig.json
.git/
.DS_Store
docs/
```

**Step 3: Commit**

```bash
git add README.md .npmignore
git commit -m "docs: add README and npm configuration"
```

---

## Task 15: Final Testing and Packaging

**Files:**
- Verify all tests pass
- Build production bundle
- Test installation flow

**Step 1: Run all tests**

Run: `npm test`
Expected: All tests PASS

**Step 2: Run type checking**

Run: `npm run type-check`
Expected: No errors

**Step 3: Run linting**

Run: `npm run lint`
Expected: No errors (or fix any issues)

**Step 4: Build production bundle**

Run: `npm run build`
Expected: Clean build in dist/

**Step 5: Test local installation**

Run: `npm link`
Expected: Creates global symlink

Run: `pp --help`
Expected: Shows help

Run: `pp config`
Expected: Prompts for configuration

**Step 6: Commit**

```bash
git add .
git commit -m "chore: final testing and packaging"
```

---

## Deployment

**Step 1: Publish to npm (when ready)**

```bash
npm publish
```

**Step 2: Install on Braydon's machine**

```bash
npm install -g pp-cli
pp config  # Enter API key and vault path
pp "test query"  # Verify it works
```

---

## Success Criteria

- [ ] All tests pass
- [ ] Type checking passes
- [ ] Linting passes
- [ ] Simple search works
- [ ] Interactive mode works
- [ ] Save to Obsidian works
- [ ] Config management works
- [ ] Error handling is user-friendly
- [ ] Installation is straightforward
