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
      parts.push('');
      parts.push('---');
      parts.push('');
    }

    // Question
    parts.push(`## Q: ${entry.question}`);
    parts.push('');

    // Answer with proper spacing
    parts.push(entry.answer);
    parts.push('');
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

  return parts.join('\n');
}
