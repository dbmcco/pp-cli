// ABOUTME: Types for Obsidian integration

import { Citation } from '../api/types';

export interface ConversationEntry {
  question: string;
  answer: string;
}

export interface ObsidianNote {
  title: string;
  query: string;
  conversation: ConversationEntry[];
  citations: Citation[];
}
