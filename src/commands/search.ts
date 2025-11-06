// ABOUTME: Simple search command handler

import { PerplexityClient } from '../api/client';

export async function simpleSearch(
  client: PerplexityClient,
  query: string
): Promise<string> {
  const result = await client.query(query);
  return result.content;
}
