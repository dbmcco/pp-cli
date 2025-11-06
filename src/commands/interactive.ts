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
