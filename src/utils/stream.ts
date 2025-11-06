// ABOUTME: Stream rendering utilities

import { stripThinkTags } from './format';
import { highlight } from 'cli-highlight';
import chalk from 'chalk';

/**
 * Manages streaming text output to terminal with syntax highlighting
 */
export class StreamRenderer {
  private buffer = '';
  private thinkTagOpen = false;
  private lastWrittenPos = 0;
  private inCodeBlock = false;
  private codeBlockLang = '';
  private codeBlockContent = '';

  write(chunk: string): void {
    this.buffer += chunk;

    // Check if we're inside think tags
    const thinkOpenMatches = this.buffer.match(/<think>/g);
    const thinkCloseMatches = this.buffer.match(/<\/think>/g);
    const openCount = thinkOpenMatches?.length || 0;
    const closeCount = thinkCloseMatches?.length || 0;

    this.thinkTagOpen = openCount > closeCount;

    // Skip writing if inside think tags
    if (this.thinkTagOpen) {
      return;
    }

    // Strip think tags from buffer
    const cleaned = stripThinkTags(this.buffer);
    const newContent = cleaned.substring(this.lastWrittenPos);

    if (!newContent) {
      return;
    }

    // Check for code blocks
    const codeBlockStart = /```(\w*)\n/g;
    const codeBlockEnd = /```/g;

    let output = '';
    let pos = 0;

    for (let i = 0; i < newContent.length; i++) {
      const remaining = newContent.substring(i);

      // Check for code block start
      if (!this.inCodeBlock && remaining.startsWith('```')) {
        const match = remaining.match(/```(\w*)\n/);
        if (match) {
          this.inCodeBlock = true;
          this.codeBlockLang = match[1] || 'text';
          this.codeBlockContent = '';
          output += chalk.dim('```') + chalk.cyan(this.codeBlockLang) + '\n';
          i += match[0].length - 1;
          continue;
        }
      }

      // Check for code block end
      if (this.inCodeBlock && remaining.startsWith('```')) {
        this.inCodeBlock = false;
        // Highlight and write the code block
        try {
          const highlighted = highlight(this.codeBlockContent, {
            language: this.codeBlockLang,
            ignoreIllegals: true
          });
          output += highlighted;
        } catch (e) {
          output += this.codeBlockContent;
        }
        output += chalk.dim('```') + '\n';
        this.codeBlockContent = '';
        i += 2; // Skip the ```
        continue;
      }

      // Accumulate code block content or write regular content
      if (this.inCodeBlock) {
        this.codeBlockContent += newContent[i];
      } else {
        output += newContent[i];
      }
    }

    if (output) {
      process.stdout.write(output);
      this.lastWrittenPos = cleaned.length;
    }
  }

  getFullContent(): string {
    return stripThinkTags(this.buffer);
  }

  clear(): void {
    this.buffer = '';
    this.thinkTagOpen = false;
    this.lastWrittenPos = 0;
    this.inCodeBlock = false;
    this.codeBlockContent = '';
  }
}
