// ABOUTME: Interactive prompts for configuration setup

import inquirer from 'inquirer';
import { Config } from './types';

export async function promptForConfig(): Promise<Config> {
  const answers = await inquirer.prompt([
    {
      type: 'password',
      name: 'apiKey',
      message: 'Perplexity API Key:',
      validate: (input: string) => {
        if (!input || input.trim().length === 0) {
          return 'API key is required';
        }
        return true;
      }
    },
    {
      type: 'input',
      name: 'vaultPath',
      message: 'Obsidian Vault Path:',
      validate: (input: string) => {
        if (!input || input.trim().length === 0) {
          return 'Vault path is required';
        }
        return true;
      }
    },
    {
      type: 'input',
      name: 'defaultModel',
      message: 'Default Perplexity Model:',
      default: 'sonar-pro'
    }
  ]);

  return answers as Config;
}
