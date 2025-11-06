// ABOUTME: Interactive mode command handler

import inquirer from 'inquirer';
import chalk from 'chalk';
import ora from 'ora';
import { PerplexityClient } from '../api/client';
import { Message } from '../api/types';
import { ObsidianWriter } from '../obsidian/writer';
import { ObsidianNote, ConversationEntry } from '../obsidian/types';
import { Citation } from '../api/types';
import { formatCitations, formatResponse } from '../utils/format';

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
  // Show spinner for research model (reasoning takes time)
  const spinner = ora({
    text: client['model'] === 'sonar-reasoning' ? chalk.dim('Thinking deeply...') : 'Searching...',
    color: 'cyan',
    spinner: 'dots'
  }).start();

  const result = await client.query(query, session.conversationHistory);

  spinner.stop();

  session.conversationHistory.push(
    { role: 'user', content: query },
    { role: 'assistant', content: result.content }
  );

  session.conversationEntries.push({
    question: query,
    answer: result.content
  });

  session.allCitations.push(...result.citations);

  // Display formatted response
  console.log(); // spacing
  const formatted = formatResponse(result.content);
  console.log(formatted);

  // Show citations
  if (result.citations.length > 0) {
    console.log(formatCitations(result.citations));
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

  // Generate slug from original query - take first 5 words
  const slug = originalQuery
    .trim()
    .split(/\s+/)
    .slice(0, 5)
    .join(' ')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .substring(0, 50); // Max 50 chars for filename safety

  // Use the original query as the title
  const note: ObsidianNote = {
    title: originalQuery,
    query: originalQuery,
    conversation: session.conversationEntries,
    citations: session.allCitations
  };

  const filename = await writer.writeNote(note, slug);
  return filename;
}
