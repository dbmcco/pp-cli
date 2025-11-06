// ABOUTME: Tests for Perplexity API client

import { describe, it, expect } from 'vitest';
import { PerplexityClient } from './client';

describe('PerplexityClient', () => {
  it('should initialize with API key and model', () => {
    const client = new PerplexityClient('test-key', 'sonar-pro');
    expect(client).toBeDefined();
  });
});
