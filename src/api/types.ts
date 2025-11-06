// ABOUTME: Type definitions for Perplexity API

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface PerplexityRequest {
  model: string;
  messages: Message[];
}

export interface Citation {
  title: string;
  url: string;
}

export interface PerplexityResponse {
  id: string;
  model: string;
  created: number;
  choices: Array<{
    index: number;
    message: Message;
    finish_reason: string;
  }>;
  citations?: Citation[];
}
