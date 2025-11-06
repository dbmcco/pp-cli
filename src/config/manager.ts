// ABOUTME: Configuration file management

import { promises as fs } from 'fs';
import * as path from 'path';
import * as os from 'os';
import { Config, DEFAULT_CONFIG_DIR, CONFIG_FILENAME } from './types';

export class ConfigManager {
  private configDir: string;
  private configPath: string;

  constructor(configDir?: string) {
    this.configDir = configDir || path.join(os.homedir(), DEFAULT_CONFIG_DIR);
    this.configPath = path.join(this.configDir, CONFIG_FILENAME);
  }

  async readConfig(): Promise<Config | null> {
    try {
      const data = await fs.readFile(this.configPath, 'utf-8');
      return JSON.parse(data) as Config;
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        return null;
      }
      throw error;
    }
  }
}
