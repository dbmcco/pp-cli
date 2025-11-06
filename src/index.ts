#!/usr/bin/env node
// ABOUTME: CLI entry point for pp-cli

import { runCLI } from './cli';

runCLI().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
