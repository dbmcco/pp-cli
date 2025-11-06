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

  async query(userQuery: string, conversationHistory: Message[] = []): Promise<QueryResult> {
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
  }
}
