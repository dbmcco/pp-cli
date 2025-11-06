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
