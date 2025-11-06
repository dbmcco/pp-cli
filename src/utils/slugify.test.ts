// ABOUTME: Tests for slug generation

import { describe, it, expect } from 'vitest';
import { slugify } from './slugify';

describe('slugify', () => {
  it('should convert text to lowercase slug', () => {
    expect(slugify('What Is Rust Ownership')).toBe('what-is-rust-ownership');
  });

  it('should replace spaces with dashes', () => {
    expect(slugify('hello world test')).toBe('hello-world-test');
  });

  it('should remove special characters', () => {
    expect(slugify('test? & example!')).toBe('test-example');
  });

  it('should truncate at word boundaries', () => {
    const longText = 'this is a very long text that should be truncated at a reasonable word boundary';
    const result = slugify(longText, 30);
    expect(result.length).toBeLessThanOrEqual(35); // Allow some buffer for word boundary
    expect(result).not.toContain(' ');
    expect(result.endsWith('-')).toBe(false);
  });

  it('should handle multiple consecutive spaces', () => {
    expect(slugify('hello    world')).toBe('hello-world');
  });
});
