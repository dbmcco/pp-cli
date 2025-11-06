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
