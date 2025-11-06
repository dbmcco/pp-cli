// ABOUTME: Response formatting utilities

import { marked } from 'marked';
import { markedTerminal } from 'marked-terminal';
import terminalLink from 'terminal-link';
import chalk from 'chalk';

// Configure marked for terminal rendering
marked.use(markedTerminal() as any);

/**
 * Strips <think>...</think> tags from reasoning model responses
 */
export function stripThinkTags(content: string): string {
  return content.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
}

/**
 * Extracts think tags and returns content + thinking separately
 */
export function extractThinking(content: string): { content: string; thinking: string | null } {
  const thinkMatch = content.match(/<think>([\s\S]*?)<\/think>/i);

  if (!thinkMatch) {
    return { content, thinking: null };
  }

  const thinking = thinkMatch[1].trim();
  const cleanedContent = content.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();

  return { content: cleanedContent, thinking };
}

/**
 * Makes URLs clickable in terminal (CMD+click to open)
 */
function makeLinksClickable(content: string): string {
  // Match markdown links: [text](url)
  const markdownLinkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
  content = content.replace(markdownLinkRegex, (match, text, url) => {
    return terminalLink(text, url, { fallback: () => `${text} (${url})` });
  });

  // Match bare URLs
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  content = content.replace(urlRegex, (url) => {
    return terminalLink(url, url, { fallback: () => url });
  });

  return content;
}

/**
 * Formats response for terminal display:
 * - Strips think tags
 * - Renders markdown
 * - Makes links clickable
 */
export function formatResponse(content: string): string {
  const cleaned = stripThinkTags(content);
  let formatted = marked(cleaned) as string;
  formatted = makeLinksClickable(formatted);
  return formatted;
}

/**
 * Formats a section header with visual separation
 */
export function formatHeader(text: string): string {
  const line = '─'.repeat(text.length + 4);
  return chalk.bold.blue(`\n${line}\n  ${text}\n${line}\n`);
}

/**
 * Formats citations for display
 */
export function formatCitations(citations: Array<{ title: string; url: string }>): string {
  if (citations.length === 0) return '';

  const header = formatHeader('Sources');
  const items = citations.map((citation, i) => {
    const link = terminalLink(
      chalk.cyan(citation.title),
      citation.url,
      { fallback: () => `${citation.title}\n  ${chalk.dim(citation.url)}` }
    );
    return `${chalk.gray(`[${i + 1}]`)} ${link}`;
  });

  return header + items.join('\n') + '\n';
}
