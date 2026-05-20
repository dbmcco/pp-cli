// ABOUTME: Runtime access to the shared Paia model route registry.
// ABOUTME: Resolves semantic route IDs from paia-agent-runtime's checked-in TOML registry.

import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';

export const PP_DEFAULT_SEARCH_ROUTE = 'pp.default_search';
export const PP_RESEARCH_ROUTE = 'pp.research';

export interface ModelRoute {
  id: string;
  owner: string;
  surface: string;
  provider: string;
  model: string;
}

let cachedRoutes: Map<string, ModelRoute> | null = null;

export function modelForRoute(routeId: string): string {
  return routeFor(routeId).model;
}

export function routeFor(routeId: string): ModelRoute {
  const normalized = routeId.trim().toLowerCase();
  const route = loadRoutes().get(normalized);
  if (!route) {
    throw new Error(`Unknown model route: ${routeId}`);
  }
  return route;
}

function loadRoutes(): Map<string, ModelRoute> {
  if (cachedRoutes) return cachedRoutes;
  const text = readFileSync(resolveRegistryPath(), 'utf8');
  cachedRoutes = parseModelRoutes(text);
  return cachedRoutes;
}

function resolveRegistryPath(): string {
  const configured = process.env.PAIA_MODEL_ROUTE_REGISTRY_PATH?.trim();
  const candidates = [
    configured,
    resolve(process.cwd(), '../paia-agent-runtime/config/cognition-presets.toml'),
    resolve(process.cwd(), '../../paia-agent-runtime/config/cognition-presets.toml'),
    resolve(process.cwd(), '../../../paia-agent-runtime/config/cognition-presets.toml')
  ].filter((candidate): candidate is string => Boolean(candidate));
  const found = candidates.find((candidate) => existsSync(candidate));
  if (!found) {
    throw new Error(
      'Unable to find central model route registry. Set PAIA_MODEL_ROUTE_REGISTRY_PATH.'
    );
  }
  return found;
}

function parseModelRoutes(text: string): Map<string, ModelRoute> {
  const routes = new Map<string, ModelRoute>();
  let activeId: string | null = null;
  let active: Record<string, string> = {};

  const flush = () => {
    if (!activeId) return;
    routes.set(activeId, {
      id: activeId,
      owner: required(active, 'owner', activeId),
      surface: required(active, 'surface', activeId),
      provider: required(active, 'provider', activeId),
      model: required(active, 'model', activeId)
    });
  };

  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    const routeHeader = line.match(/^\[model_routes\."([^"]+)"\]$/);
    if (routeHeader) {
      flush();
      activeId = routeHeader[1].trim().toLowerCase();
      active = {};
      continue;
    }
    if (line.startsWith('[') && activeId) {
      flush();
      activeId = null;
      active = {};
      continue;
    }
    if (!activeId || line === '' || line.startsWith('#')) continue;
    const assignment = line.match(/^([A-Za-z0-9_]+)\s*=\s*"([^"]*)"$/);
    if (assignment) {
      active[assignment[1]] = assignment[2];
    }
  }
  flush();
  return routes;
}

function required(values: Record<string, string>, key: string, routeId: string): string {
  const value = values[key]?.trim();
  if (!value) {
    throw new Error(`Model route ${routeId} is missing required field ${key}`);
  }
  return value;
}
