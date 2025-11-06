// ABOUTME: Simple search command handler

import { PerplexityClient } from '../api/client';
import { Citation } from '../api/types';

export interface SearchResult {
  content: string;
  citations: Citation[];
}

export async function simpleSearch(
  client: PerplexityClient,
  query: string
): Promise<SearchResult> {
  const result = await client.query(query);
  return {
    content: result.content,
    citations: result.citations
  };
}
