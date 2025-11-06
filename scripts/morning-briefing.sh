#!/bin/bash

# ABOUTME: Daily morning news briefing script for Obsidian

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get today's date for filename and context
TODAY=$(date +"%Y-%m-%d")
BRIEFING_DATE=$(date +"%A, %B %d, %Y")
DAY_OF_WEEK=$(date +"%A" | tr '[:upper:]' '[:lower:]')

# Obsidian vault path (relative to vault root)
VAULT_PATH="daily-briefings/${TODAY}-news-briefing.md"

# Select the appropriate prompt file based on day of week
PROMPT_FILE="${SCRIPT_DIR}/prompts/${DAY_OF_WEEK}.md"

# Check if prompt file exists
if [ ! -f "$PROMPT_FILE" ]; then
  echo "Error: Prompt file not found: $PROMPT_FILE"
  exit 1
fi

# Read prompt from file and replace {DATE} placeholder
PROMPT=$(cat "$PROMPT_FILE" | sed "s/{DATE}/${BRIEFING_DATE}/g")

# Run pp-cli with research mode for comprehensive coverage
pp -r --no-interactive "$PROMPT" --save-to "$VAULT_PATH" --output text

# Exit with the same code as pp
exit $?
