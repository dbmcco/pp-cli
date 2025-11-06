// ABOUTME: Perplexity API client

import axios, { AxiosInstance } from 'axios';
import { PerplexityRequest, PerplexityResponse, Message } from './types';

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
}
