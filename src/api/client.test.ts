// ABOUTME: Tests for Perplexity API client

import { vi, describe, it, expect, beforeEach } from 'vitest';
import axios from 'axios';
import { PerplexityClient } from './client';
import { modelForRoute, PP_DEFAULT_SEARCH_ROUTE } from '../model-routes';

vi.mock('axios');
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const mockedAxios = axios as any;

describe('PerplexityClient', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with API key and model', () => {
    const client = new PerplexityClient('test-key', modelForRoute(PP_DEFAULT_SEARCH_ROUTE));
    expect(client).toBeDefined();
  });

  describe('query', () => {
    it('should send query and return response', async () => {
      const mockResponse = {
        data: {
          id: 'test-id',
          model: modelForRoute(PP_DEFAULT_SEARCH_ROUTE),
          created: 123456,
          choices: [{
            index: 0,
            message: {
              role: 'assistant',
              content: 'Test response'
            },
            finish_reason: 'stop'
          }],
          citations: ['https://example.com']
        }
      };

      mockedAxios.create.mockReturnValue({
        post: vi.fn().mockResolvedValue(mockResponse)
      });

      const client = new PerplexityClient('test-key', modelForRoute(PP_DEFAULT_SEARCH_ROUTE));
      const result = await client.query('test query');

      expect(result.content).toBe('Test response');
      expect(result.citations).toHaveLength(1);
      expect(result.citations[0].title).toBe('example.com');
    });
  });
});
