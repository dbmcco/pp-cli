#!/bin/bash

# ABOUTME: Daily morning news briefing script for Obsidian

# Get today's date for filename and context
TODAY=$(date +"%Y-%m-%d")
BRIEFING_DATE=$(date +"%A, %B %d, %Y")

# Obsidian vault path (relative to vault root)
VAULT_PATH="daily-briefings/${TODAY}-news-briefing.md"

# Comprehensive news briefing prompt
PROMPT="Generate a comprehensive morning news briefing for ${BRIEFING_DATE}. Structure the briefing as follows:

## Top Headlines
Summarize the 3-5 most important global news stories today

## Technology & AI
Key developments in technology, AI, and software

## Business & Markets
Major business news, market movements, and economic indicators

## Science & Health
Notable scientific breakthroughs, health news, or research

## Notable Events
Any significant political, social, or cultural events

For each section, provide:
- Clear, concise summaries
- Why it matters
- Key takeaways

Keep the total briefing concise (500-800 words) but informative."

# Run pp-cli with research mode for comprehensive coverage
pp -r --no-interactive "$PROMPT" --save-to "$VAULT_PATH" --output text

# Exit with the same code as pp
exit $?
