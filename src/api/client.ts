// ABOUTME: Perplexity API client

import axios, { AxiosInstance } from 'axios';
import { PerplexityRequest, PerplexityResponse, Message, Citation } from './types';

export interface QueryResult {
  content: string;
  citations: Citation[];
}

export class PerplexityClient {
  private apiKey: string;
  private model: string;
  private client: AxiosInstance;

  constructor(apiKey: string, model: string = 'sonar-pro') {
    this.apiKey = apiKey;
    this.model = model;
    this.client = axios.create({
      baseURL: 'https://api.perplexity.ai',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      }
    });
  }

  private async retryWithBackoff<T>(
    fn: () => Promise<T>,
    maxRetries: number = 3
  ): Promise<T> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;

        // Don't retry on auth errors
        if (axios.isAxiosError(error) && error.response?.status === 401) {
          throw new Error('Invalid API key. Run `pp config` to update.');
        }

        // Don't retry on rate limit errors
        if (axios.isAxiosError(error) && error.response?.status === 429) {
          const retryAfter = error.response.headers['retry-after'] || '60';
          throw new Error(`Rate limit hit. Try again in ${retryAfter} seconds.`);
        }

        // Wait before retrying
        if (attempt < maxRetries - 1) {
          const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    throw lastError || new Error('Request failed');
  }

  async query(userQuery: string, conversationHistory: Message[] = []): Promise<QueryResult> {
    return this.retryWithBackoff(async () => {
      const messages: Message[] = [
        ...conversationHistory,
        { role: 'user', content: userQuery }
      ];

      const request: PerplexityRequest = {
        model: this.model,
        messages
      };

      const response = await this.client.post<PerplexityResponse>('/chat/completions', request);

      return {
        content: response.data.choices[0].message.content,
        citations: response.data.citations || []
      };
    });
  }
}
