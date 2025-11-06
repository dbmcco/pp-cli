// ABOUTME: Tests for configuration management

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { promises as fs } from 'fs';
import * as path from 'path';
import * as os from 'os';
import { ConfigManager } from './manager';

describe('ConfigManager', () => {
  let testConfigDir: string;
  let configManager: ConfigManager;

  beforeEach(async () => {
    // Create temp config directory
    testConfigDir = path.join(os.tmpdir(), `pp-test-${Date.now()}`);
    await fs.mkdir(testConfigDir, { recursive: true });
    configManager = new ConfigManager(testConfigDir);
  });

  afterEach(async () => {
    // Clean up
    await fs.rm(testConfigDir, { recursive: true, force: true });
  });

  describe('readConfig', () => {
    it('should return null when config file does not exist', async () => {
      const config = await configManager.readConfig();
      expect(config).toBeNull();
    });

    it('should read and parse existing config file', async () => {
      const expectedConfig = {
        apiKey: 'test-key',
        vaultPath: '/test/path',
        defaultModel: 'sonar-pro'
      };

      const configPath = path.join(testConfigDir, 'config.json');
      await fs.writeFile(configPath, JSON.stringify(expectedConfig));

      const config = await configManager.readConfig();
      expect(config).toEqual(expectedConfig);
    });
  });

  describe('writeConfig', () => {
    it('should create config directory if it does not exist', async () => {
      await fs.rm(testConfigDir, { recursive: true, force: true });

      const config = {
        apiKey: 'test-key',
        vaultPath: '/test/path',
        defaultModel: 'sonar-pro'
      };

      await configManager.writeConfig(config);

      const exists = await fs.access(testConfigDir).then(() => true).catch(() => false);
      expect(exists).toBe(true);
    });

    it('should write config to file', async () => {
      const config = {
        apiKey: 'test-key',
        vaultPath: '/test/path',
        defaultModel: 'sonar-pro'
      };

      await configManager.writeConfig(config);

      const configPath = path.join(testConfigDir, 'config.json');
      const data = await fs.readFile(configPath, 'utf-8');
      expect(JSON.parse(data)).toEqual(config);
    });
  });
});
