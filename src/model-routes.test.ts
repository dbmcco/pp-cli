// ABOUTME: Tests for resolving pp semantic routes through the central registry.

import { describe, expect, it } from 'vitest';
import { modelForRoute, PP_DEFAULT_SEARCH_ROUTE, PP_RESEARCH_ROUTE } from './model-routes';

describe('model routes', () => {
  it('resolves pp routes to current Perplexity models', () => {
    expect(modelForRoute(PP_DEFAULT_SEARCH_ROUTE)).toBe('sonar-pro');
    expect(modelForRoute(PP_RESEARCH_ROUTE)).toBe('sonar-reasoning');
  });
});
