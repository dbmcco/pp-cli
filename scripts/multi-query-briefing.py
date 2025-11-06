#!/usr/bin/env python3

# ABOUTME: Multi-query morning briefing - runs separate queries per section

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

def run_query(query: str) -> str:
    """Run a single pp query and return the result"""
    try:
        result = subprocess.run(
            ['pp', '--no-interactive', query, '--output', 'markdown'],
            capture_output=True,
            text=True,
            timeout=60
        )
        # Filter out progress indicators
        lines = result.stdout.split('\n')
        content = '\n'.join(line for line in lines
                          if not line.startswith(('- ', 'Searching', 'Thinking')))
        return content.strip()
    except Exception as e:
        print(f"Error running query: {e}", file=sys.stderr)
        return ""

def parse_queries_file(file_path: str) -> list[tuple[str, str]]:
    """Parse the queries file into (section_name, query) tuples"""
    queries = []
    current_section = None
    current_query = []

    with open(file_path, 'r') as f:
        for line in f:
            line = line.rstrip()

            if line.startswith('SECTION:'):
                # Save previous section if exists
                if current_section and current_query:
                    queries.append((current_section, '\n'.join(current_query)))

                # Start new section
                current_section = line.split(':', 1)[1].strip()
                current_query = []
            elif current_section and line:  # Non-empty line in a section
                current_query.append(line)

        # Don't forget the last section
        if current_section and current_query:
            queries.append((current_section, '\n'.join(current_query)))

    return queries

def main():
    # Get script directory and dates
    script_dir = Path(__file__).parent
    today = datetime.now().strftime('%Y-%m-%d')
    briefing_date = datetime.now().strftime('%A, %B %d, %Y')
    day_of_week = datetime.now().strftime('%A').lower()

    # Paths
    queries_file = script_dir / 'prompts' / f'{day_of_week}-queries.md'
    vault_path = Path('/Users/braydon/Obsidian/Bvault/daily-briefings') / f'{today}-news-briefing.md'

    # Check if queries file exists
    if not queries_file.exists():
        print(f"Error: Queries file not found: {queries_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Generating briefing for {briefing_date}...")

    # Parse queries
    queries = parse_queries_file(str(queries_file))

    # Run each query
    results = []
    for section_name, query in queries:
        print(f"  Querying: {section_name}...")
        result = run_query(query)
        if result:
            results.append((section_name, result))

    # Combine into final note
    print("Combining sections...")

    vault_path.parent.mkdir(parents=True, exist_ok=True)

    with open(vault_path, 'w') as f:
        # Frontmatter
        f.write('---\n')
        f.write(f'created: {datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}\n')
        f.write('query: "Morning Briefing"\n')
        f.write('tags: [briefing, daily, perplexity]\n')
        f.write('---\n\n')

        # Title
        f.write(f'# Morning Briefing - {briefing_date}\n\n')

        # Sections
        for section_name, content in results:
            f.write(f'## {section_name}\n\n')
            f.write(f'{content}\n\n')

    print(f"✓ Briefing saved to: daily-briefings/{today}-news-briefing.md")

if __name__ == '__main__':
    main()
