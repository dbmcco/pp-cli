// ABOUTME: CLI command handling

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import * as path from 'path';
import { promises as fs } from 'fs';
import { ConfigManager } from './config/manager';
import { PerplexityClient } from './api/client';
import { ObsidianWriter } from './obsidian/writer';
import { startInteractiveSession, promptToSave } from './commands/interactive';
import { formatResponse, formatCitations, extractThinking } from './utils/format';

export async function runCLI() {
  const program = new Command();

  program
    .name('pp')
    .description('Perplexity CLI search tool - conversational AI-powered search')
    .version('0.1.0');

  program
    .argument('[query...]', 'search query')
    .option('-r, --research', 'deep research mode with reasoning model')
    .option('--no-interactive', 'non-interactive mode for scripting (skips follow-up prompts)')
    .option('--output <format>', 'output format: text (default), json, markdown')
    .option('--save-to <path>', 'save to specific Obsidian note path (relative to vault)')
    .option('--append-to <path>', 'append results to existing note (relative to vault)')
    .action(async (queryParts: string[], options: {
      research?: boolean;
      interactive?: boolean;
      output?: string;
      saveTo?: string;
      appendTo?: string;
    }) => {
      let query = queryParts.join(' ').trim();

      try {
        // Load config
        const configManager = new ConfigManager();
        const config = await configManager.getOrSetupConfig();

        // If no query provided and in interactive mode, prompt for input
        if (!query && options.interactive !== false) {
          console.log(chalk.cyan('Enter your query (paste anything, then press Enter):'));
          process.stdout.write(chalk.cyan('> '));

          // Use raw stdin reading to avoid readline launching editors
          query = await new Promise<string>((resolve) => {
            let buffer = '';
            const onData = (chunk: Buffer) => {
              const text = chunk.toString();
              // Look for newline to indicate end of input
              if (text.includes('\n')) {
                process.stdin.removeListener('data', onData);
                process.stdin.pause();
                // Get everything up to the first newline
                const lines = (buffer + text).split('\n');
                resolve(lines[0].trim());
              } else {
                buffer += text;
              }
            };

            process.stdin.setEncoding('utf8');
            process.stdin.on('data', onData);
            process.stdin.resume();
          });

          if (!query) {
            console.log(chalk.yellow('No query provided. Exiting.'));
            process.exit(0);
          }
        }

        // Still no query? Exit gracefully
        if (!query) {
          console.log(chalk.yellow('No query provided. Use: pp "your query here"'));
          process.exit(0);
        }

        // Use research model if -r flag is set
        const model = options.research ? 'sonar-reasoning' : config.defaultModel;

        // Initialize client and writer
        const client = new PerplexityClient(config.apiKey, model);
        const writer = new ObsidianWriter(config.vaultPath);

        // Non-interactive mode for scripting
        if (options.interactive === false) {
          const spinner = ora({
            text: options.research ? 'Researching...' : 'Searching...',
            color: 'cyan',
            spinner: 'dots'
          }).start();

          const result = await client.query(query);
          spinner.stop();

          // Format output based on --output flag
          const outputFormat = options.output || 'text';

          if (outputFormat === 'json') {
            // JSON output for Claude Code to parse
            console.log(JSON.stringify({
              query,
              answer: result.content,
              citations: result.citations,
              model
            }, null, 2));
          } else if (outputFormat === 'markdown') {
            // Raw markdown without terminal formatting
            console.log(result.content);
            if (result.citations.length > 0) {
              console.log('\n## Sources\n');
              result.citations.forEach((c, i) => {
                console.log(`${i + 1}. [${c.title}](${c.url})`);
              });
            }
          } else {
            // Default text output with formatting
            const formatted = formatResponse(result.content);
            console.log(formatted);
            if (result.citations.length > 0) {
              console.log(formatCitations(result.citations));
            }
          }

          // Handle save options
          if (options.saveTo || options.appendTo) {
            const targetPath = options.saveTo || options.appendTo;
            const fullPath = path.join(config.vaultPath, targetPath!);

            if (options.appendTo) {
              // Append to existing note with thinking at bottom if present
              const { content, thinking } = extractThinking(result.content);

              let appendContent = `\n\n---\n\n# ${query}\n\n${content}\n`;

              // Add thinking section if present
              if (thinking) {
                appendContent += `\n## Reasoning\n\n*Internal reasoning:*\n\n${thinking}\n`;
              }

              await fs.appendFile(fullPath, appendContent, 'utf-8');
              if (!outputFormat || outputFormat === 'text') {
                console.log(chalk.green(`\n✓ Appended to: ${targetPath}`));
              }
            } else {
              // Save as new note
              const note = {
                title: query,
                query,
                conversation: [{ question: query, answer: result.content }],
                citations: result.citations
              };
              await writer.writeNote(note, path.basename(targetPath!, '.md'));
              if (!outputFormat || outputFormat === 'text') {
                console.log(chalk.green(`\n✓ Saved to: ${targetPath}`));
              }
            }
          }
        } else {
          // Interactive mode (default)
          const session = await startInteractiveSession(client, query);

          // Prompt to save conversation
          const filename = await promptToSave(session, client, writer, query);

          if (filename) {
            console.log(chalk.green(`\n✓ Saved to: ${filename}`));
          }
        }
      } catch (error) {
        console.error(chalk.red('Error:'), (error as Error).message);
        process.exit(1);
      }
    });

  program
    .command('config')
    .description('Configure pp-cli')
    .action(async () => {
      try {
        const configManager = new ConfigManager();
        const config = await configManager.setupConfig();
        console.log(chalk.green('✓ Configuration saved'));
        console.log('API Key:', config.apiKey.substring(0, 10) + '...');
        console.log('Vault Path:', config.vaultPath);
        console.log('Model:', config.defaultModel);
      } catch (error) {
        console.error(chalk.red('Error:'), (error as Error).message);
        process.exit(1);
      }
    });

  await program.parseAsync(process.argv);
}
