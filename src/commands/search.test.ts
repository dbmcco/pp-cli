// ABOUTME: Tests for simple search command

import { describe, it, expect, vi } from 'vitest';
import { simpleSearch } from './search';
import { PerplexityClient } from '../api/client';

vi.mock('../api/client');

describe('simpleSearch', () => {
  it('should query API and return formatted response', async () => {
    const mockQuery = vi.fn().mockResolvedValue({
      content: 'Test response',
      citations: []
    });

    const mockClient = {
      query: mockQuery
    } as unknown as PerplexityClient;

    const result = await simpleSearch(mockClient, 'test query');

    expect(mockQuery).toHaveBeenCalledWith('test query', []);
    expect(result).toBe('Test response');
  });
});
