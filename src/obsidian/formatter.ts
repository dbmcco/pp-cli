// ABOUTME: Markdown formatting for Obsidian notes

import { ObsidianNote } from './types';
import { extractThinking } from '../utils/format';

export function formatAsMarkdown(note: ObsidianNote): string {
  const now = new Date().toISOString();

  const parts: string[] = [];
  const thinkingParts: Array<{ question: string; thinking: string }> = [];

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
      parts.push('');
      parts.push('---');
      parts.push('');
    }

    // Question
    parts.push(`## Q: ${entry.question}`);
    parts.push('');

    // Extract thinking from answer
    const { content, thinking } = extractThinking(entry.answer);

    // Answer with proper spacing (thinking removed)
    parts.push(content);
    parts.push('');

    // Collect thinking for bottom section
    if (thinking) {
      thinkingParts.push({ question: entry.question, thinking });
    }
  });

  // Citations
  if (note.citations.length > 0) {
    parts.push('');
    parts.push('---');
    parts.push('');
    parts.push('## Sources');
    parts.push('');

    // Remove duplicates and format
    const uniqueCitations = Array.from(
      new Map(note.citations.map(c => [c.url, c])).values()
    );

    uniqueCitations.forEach((citation, index) => {
      parts.push(`${index + 1}. [${citation.title}](${citation.url})`);
    });
    parts.push('');
  }

  // Reasoning (thinking) section at bottom
  if (thinkingParts.length > 0) {
    parts.push('');
    parts.push('---');
    parts.push('');
    parts.push('## Reasoning');
    parts.push('');
    parts.push('*Internal reasoning from the AI model:*');
    parts.push('');

    thinkingParts.forEach((item, index) => {
      if (index > 0) {
        parts.push('');
      }
      parts.push(`### Re: ${item.question}`);
      parts.push('');
      parts.push(item.thinking);
      parts.push('');
    });
  }

  return parts.join('\n');
}
