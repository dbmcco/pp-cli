// ABOUTME: CLI command handling

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { ConfigManager } from './config/manager';
import { PerplexityClient } from './api/client';
import { ObsidianWriter } from './obsidian/writer';
import { simpleSearch } from './commands/search';
import { startInteractiveSession, promptToSave } from './commands/interactive';
import { formatResponse, formatCitations } from './utils/format';

export async function runCLI() {
  const program = new Command();

  program
    .name('pp')
    .description('Perplexity CLI search tool')
    .version('0.1.0');

  program
    .argument('[query...]', 'search query')
    .option('-i, --interactive', 'interactive mode with conversation')
    .option('-r, --research', 'deep research mode with comprehensive analysis')
    .action(async (queryParts: string[], options: { interactive?: boolean; research?: boolean }) => {
      const query = queryParts.join(' ');
      try {
        // Load config
        const configManager = new ConfigManager();
        const config = await configManager.getOrSetupConfig();

        // Use research model if -r flag is set
        const model = options.research ? 'sonar-reasoning' : config.defaultModel;

        // Research mode always enables interactive
        const isInteractive = options.interactive || options.research;

        // Initialize client and writer
        const client = new PerplexityClient(config.apiKey, model);
        const writer = new ObsidianWriter(config.vaultPath);

        if (isInteractive) {
          // Interactive mode
          const session = await startInteractiveSession(
            client,
            query,
            (content, citations) => {
              console.log(); // spacing
              const formatted = formatResponse(content);
              console.log(formatted);

              // Show citations if available
              if (citations.length > 0) {
                const citationsFormatted = formatCitations(citations);
                console.log(citationsFormatted);
              }

              console.log(); // spacing after response
            }
          );

          // Prompt to save conversation
          const filename = await promptToSave(session, client, writer, query);

          if (filename) {
            console.log(chalk.green(`\n✓ Saved to: ${filename}`));
          }
        } else {
          // Simple search
          const spinner = ora({
            text: 'Searching...',
            color: 'cyan',
            spinner: 'dots'
          }).start();

          const result = await simpleSearch(client, query);
          spinner.stop();

          console.log(); // spacing
          const formatted = formatResponse(result.content);
          console.log(formatted);

          // Show citations if available
          if (result.citations.length > 0) {
            const citationsFormatted = formatCitations(result.citations);
            console.log(citationsFormatted);
          }

          console.log(); // spacing
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
