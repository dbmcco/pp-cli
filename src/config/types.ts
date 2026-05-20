// ABOUTME: Type definitions for configuration

export interface Config {
  apiKey: string;
  vaultPath: string;
  defaultRoute?: string;
  defaultModel?: string;
}

export const DEFAULT_CONFIG_DIR = '.config/pp';
export const CONFIG_FILENAME = 'config.json';
