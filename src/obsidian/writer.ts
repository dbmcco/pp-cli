// ABOUTME: Obsidian file writer

import { promises as fs } from 'fs';
import * as path from 'path';
import { ObsidianNote } from './types';
import { formatAsMarkdown } from './formatter';

export class ObsidianWriter {
  private vaultPath: string;

  constructor(vaultPath: string) {
    this.vaultPath = vaultPath;
  }

  async writeNote(note: ObsidianNote, slug: string): Promise<string> {
    // Generate filename with date
    const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    let filename = `${date}-${slug}.md`;
    let filepath = path.join(this.vaultPath, filename);

    // Handle collisions
    let counter = 2;
    while (await this.fileExists(filepath)) {
      filename = `${date}-${slug}-${counter}.md`;
      filepath = path.join(this.vaultPath, filename);
      counter++;
    }

    // Write file
    const content = formatAsMarkdown(note);
    await fs.mkdir(this.vaultPath, { recursive: true });
    await fs.writeFile(filepath, content, 'utf-8');

    return filename;
  }

  private async fileExists(filepath: string): Promise<boolean> {
    try {
      await fs.access(filepath);
      return true;
    } catch {
      return false;
    }
  }
}
