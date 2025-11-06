#!/usr/bin/env python3

# ABOUTME: Multi-query morning briefing - runs separate queries per section

import subprocess
import sys
import os
import re
from datetime import datetime
from pathlib import Path

def run_query(query: str) -> tuple[str, list[tuple[str, str]]]:
    """Run a single pp query and return (content, citations) tuple"""
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

        # Split content from citations
        if '## Sources' in content:
            parts = content.split('## Sources', 1)
            main_content = parts[0].strip()
            sources_section = parts[1].strip()

            # Extract citations from sources section
            citations = []
            for line in sources_section.split('\n'):
                # Match pattern: 1. [domain.com](url)
                match = re.match(r'\d+\.\s+\[([^\]]+)\]\(([^\)]+)\)', line)
                if match:
                    citations.append((match.group(1), match.group(2)))

            return main_content, citations

        return content.strip(), []
    except Exception as e:
        print(f"Error running query: {e}", file=sys.stderr)
        return "", []

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

def renumber_citations(content: str, citation_map: dict[int, int]) -> str:
    """Renumber citations in content according to citation_map"""
    # Replace [N] with new numbers
    def replace_cite(match):
        old_num = int(match.group(1))
        new_num = citation_map.get(old_num, old_num)
        return f'[{new_num}]'

    return re.sub(r'\[(\d+)\]', replace_cite, content)

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

    # Run each query and collect all citations
    results = []
    all_citations = []
    weather_content = None
    weather_section_name = None

    for section_name, query in queries:
        print(f"  Querying: {section_name}...")
        content, citations = run_query(query)

        # Handle weather separately - put it at the top
        if 'weather' in section_name.lower():
            weather_section_name = section_name
            weather_content = content
            continue

        if content:
            # Build citation map for this section
            citation_map = {}
            section_citations = []

            for i, (domain, url) in enumerate(citations, 1):
                # Check if we already have this citation
                global_idx = None
                for idx, (d, u) in enumerate(all_citations, 1):
                    if u == url:
                        global_idx = idx
                        break

                if global_idx is None:
                    # New citation
                    all_citations.append((domain, url))
                    global_idx = len(all_citations)

                citation_map[i] = global_idx

            # Renumber citations in content
            content = renumber_citations(content, citation_map)
            results.append((section_name, content))

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

        # Weather first (compact)
        if weather_content:
            f.write(f'**Weather** (Old Lyme, CT): {weather_content}\n\n')
            f.write('---\n\n')

        # All other sections
        for section_name, content in results:
            f.write(f'## {section_name}\n\n')
            f.write(f'{content}\n\n')

        # References at the bottom
        if all_citations:
            f.write('---\n\n')
            f.write('## References\n\n')
            for i, (domain, url) in enumerate(all_citations, 1):
                f.write(f'{i}. [{domain}]({url})\n')

    print(f"✓ Briefing saved to: daily-briefings/{today}-news-briefing.md")

if __name__ == '__main__':
    main()
