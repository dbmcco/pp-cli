// ABOUTME: Response formatting utilities

import { marked } from 'marked';
import { markedTerminal } from 'marked-terminal';

// Configure marked for terminal rendering
marked.use(markedTerminal() as any);

/**
 * Strips <think>...</think> tags from reasoning model responses
 */
export function stripThinkTags(content: string): string {
  return content.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
}

/**
 * Formats response for terminal display:
 * - Strips think tags
 * - Renders markdown
 */
export function formatResponse(content: string): string {
  const cleaned = stripThinkTags(content);
  return marked(cleaned) as string;
}
