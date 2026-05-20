#!/bin/bash
# ABOUTME: Wrapper script for cron/launchd to run morning briefing
# ABOUTME: Supports both RSS-powered (default) and legacy Perplexity-only modes

# Set PATH to include homebrew binaries (needed for node/pp CLI)
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

# Change to the project directory
SCRIPT_DIR="/Users/braydon/projects/experiments/pp/scripts"
cd "$SCRIPT_DIR"

# Source environment variables if .env exists
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

# Python interpreter from venv
PYTHON="$SCRIPT_DIR/venv/bin/python3"

# Default to RSS-powered briefing, use --legacy for old behavior
if [ "$1" = "--legacy" ]; then
    echo "$(date): Running legacy Perplexity-only briefing"
    $PYTHON multi-query-briefing.py
else
    echo "$(date): Running RSS-powered briefing"
    $PYTHON rss_briefing.py
fi

# Log completion
echo "$(date): Morning briefing completed" >> /tmp/morning-briefing.log
