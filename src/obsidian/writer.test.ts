// ABOUTME: Tests for Obsidian file writing

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { promises as fs } from 'fs';
import * as path from 'path';
import * as os from 'os';
import { ObsidianWriter } from './writer';
import { ObsidianNote } from './types';

describe('ObsidianWriter', () => {
  let testDir: string;
  let writer: ObsidianWriter;

  beforeEach(async () => {
    testDir = path.join(os.tmpdir(), `pp-obsidian-test-${Date.now()}`);
    await fs.mkdir(testDir, { recursive: true });
    writer = new ObsidianWriter(testDir);
  });

  afterEach(async () => {
    await fs.rm(testDir, { recursive: true, force: true });
  });

  describe('writeNote', () => {
    it('should write note to file with correct filename', async () => {
      const note: ObsidianNote = {
        title: 'Test Topic',
        query: 'test query',
        conversation: [
          { question: 'test query', answer: 'test answer' }
        ],
        citations: []
      };

      const filename = await writer.writeNote(note, 'test-topic');

      expect(filename).toMatch(/^\d{4}-\d{2}-\d{2}-test-topic\.md$/);

      const filepath = path.join(testDir, filename);
      const exists = await fs.access(filepath).then(() => true).catch(() => false);
      expect(exists).toBe(true);
    });

    it('should handle filename collisions', async () => {
      const note: ObsidianNote = {
        title: 'Test Topic',
        query: 'test query',
        conversation: [
          { question: 'test query', answer: 'test answer' }
        ],
        citations: []
      };

      const filename1 = await writer.writeNote(note, 'test-topic');
      const filename2 = await writer.writeNote(note, 'test-topic');

      expect(filename1).not.toBe(filename2);
      expect(filename2).toMatch(/-2\.md$/);
    });
  });
});
