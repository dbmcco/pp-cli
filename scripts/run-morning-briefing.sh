#!/bin/bash
# ABOUTME: Wrapper script for cron to run morning briefing

# Change to the project directory
cd /Users/braydon/projects/experiments/pp

# Run the Python script
/opt/homebrew/bin/python3 scripts/multi-query-briefing.py

# Log completion
echo "$(date): Morning briefing completed" >> /tmp/morning-briefing.log
