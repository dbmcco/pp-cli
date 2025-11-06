#!/bin/bash

# ABOUTME: Daily morning news briefing script for Obsidian using multi-query approach

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run the multi-query briefing Python script
python3 "${SCRIPT_DIR}/multi-query-briefing.py"

# Exit with the same code as the Python script
exit $?
