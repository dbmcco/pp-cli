// ABOUTME: Interactive mode command handler

import inquirer from 'inquirer';
import chalk from 'chalk';
import ora from 'ora';
import { PerplexityClient } from '../api/client';
import { Message } from '../api/types';
import { ObsidianWriter } from '../obsidian/writer';
import { ObsidianNote, ConversationEntry } from '../obsidian/types';
import { Citation } from '../api/types';
import { formatCitations } from '../utils/format';
import { StreamRenderer } from '../utils/stream';

export interface InteractiveSession {
  conversationHistory: Message[];
  conversationEntries: ConversationEntry[];
  allCitations: Citation[];
}

export async function startInteractiveSession(
  client: PerplexityClient,
  initialQuery: string
): Promise<InteractiveSession> {
  // Check for TTY to prevent crashes in non-interactive environments
  if (!process.stdin.isTTY) {
    throw new Error('Interactive mode requires a TTY. Run from a terminal, not a pipe.');
  }

  const session: InteractiveSession = {
    conversationHistory: [],
    conversationEntries: [],
    allCitations: []
  };

  // Handle initial query
  await handleQuery(client, initialQuery, session);

  // Interactive loop
  // eslint-disable-next-line no-constant-condition
  while (true) {
    const { input } = await inquirer.prompt([
      {
        type: 'input',
        name: 'input',
        message: chalk.dim('>'),
        prefix: ''
      }
    ]);

    const trimmed = input.trim().toLowerCase();
    if (trimmed === 'exit' || trimmed === 'quit') {
      break;
    }

    if (input.trim()) {
      await handleQuery(client, input, session);
    }
  }

  return session;
}

async function handleQuery(
  client: PerplexityClient,
  query: string,
  session: InteractiveSession
): Promise<void> {
  const renderer = new StreamRenderer();
  let citations: Citation[] = [];

  // Show spinner for research model (reasoning takes time)
  const spinner = client['model'] === 'sonar-reasoning'
    ? ora({ text: chalk.dim('Thinking deeply...'), color: 'cyan', spinner: 'dots' }).start()
    : null;

  console.log(); // spacing

  const fullContent = await client.queryStream(
    query,
    {
      onChunk: (chunk: string) => {
        if (spinner) {
          spinner.stop();
          spinner.clear();
        }
        renderer.write(chunk);
      },
      onComplete: (cites: Citation[]) => {
        citations = cites;
      }
    },
    session.conversationHistory
  );

  const cleanedContent = renderer.getFullContent();

  session.conversationHistory.push(
    { role: 'user', content: query },
    { role: 'assistant', content: cleanedContent }
  );

  session.conversationEntries.push({
    question: query,
    answer: cleanedContent
  });

  session.allCitations.push(...citations);

  // Show citations after streaming completes
  console.log(); // spacing
  if (citations.length > 0) {
    console.log(formatCitations(citations));
  }
  console.log(); // spacing
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
