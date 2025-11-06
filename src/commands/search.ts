// ABOUTME: Simple search command handler

import { PerplexityClient } from '../api/client';
import { Citation } from '../api/types';
import { StreamRenderer } from '../utils/stream';

export interface SearchResult {
  content: string;
  citations: Citation[];
}

export async function simpleSearch(
  client: PerplexityClient,
  query: string
): Promise<SearchResult> {
  const renderer = new StreamRenderer();
  let citations: Citation[] = [];

  await client.queryStream(
    query,
    {
      onChunk: (chunk: string) => {
        renderer.write(chunk);
      },
      onComplete: (cites: Citation[]) => {
        citations = cites;
      }
    }
  );

  return {
    content: renderer.getFullContent(),
    citations
  };
}
