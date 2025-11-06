// ABOUTME: Perplexity API client

import axios, { AxiosInstance } from 'axios';
import { PerplexityRequest, PerplexityResponse, Message, Citation } from './types';

export interface QueryResult {
  content: string;
  citations: Citation[];
}

export interface StreamCallbacks {
  onChunk: (chunk: string) => void;
  onComplete: (citations: Citation[]) => void;
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

  async queryStream(
    userQuery: string,
    callbacks: StreamCallbacks,
    conversationHistory: Message[] = []
  ): Promise<string> {
    return this.retryWithBackoff(async () => {
      const messages: Message[] = [
        ...conversationHistory,
        { role: 'user', content: userQuery }
      ];

      const request = {
        model: this.model,
        messages,
        stream: true
      };

      const response = await this.client.post('/chat/completions', request, {
        responseType: 'stream'
      });

      let fullContent = '';
      let citations: Citation[] = [];

      return new Promise<string>((resolve, reject) => {
        response.data.on('data', (chunk: Buffer) => {
          const lines = chunk.toString().split('\n').filter(line => line.trim() !== '');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);

              if (data === '[DONE]') {
                callbacks.onComplete(citations);
                resolve(fullContent);
                return;
              }

              try {
                const parsed = JSON.parse(data);

                // Extract content delta
                const delta = parsed.choices?.[0]?.delta?.content;
                if (delta) {
                  fullContent += delta;
                  callbacks.onChunk(delta);
                }

                // Extract citations from final message
                if (parsed.citations) {
                  citations = parsed.citations;
                }
              } catch (e) {
                // Skip malformed JSON
              }
            }
          }
        });

        response.data.on('error', (error: Error) => {
          reject(error);
        });

        response.data.on('end', () => {
          callbacks.onComplete(citations);
          resolve(fullContent);
        });
      });
    });
  }
}
