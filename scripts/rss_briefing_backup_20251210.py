#!/Users/braydon/projects/experiments/pp/scripts/venv/bin/python3

# ABOUTME: RSS-powered morning briefing with LLM summarization
# ABOUTME: Hybrid approach: RSS feeds + Claude/Perplexity for synthesis

import subprocess
import sys
import os
import re
import shutil
import urllib.request
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

# Local imports
from rss_config import get_section_config, SECTION_FEEDS, DEEP_DIVE_SCHEDULE, DEEP_DIVE_PROMPTS
from rss_parser import fetch_section_feeds, format_items_for_llm, format_items_as_markdown
from llm_processor import process_rss_content, PP_CLI


def get_weather() -> str:
    """Get weather from weather.gov API for Old Lyme, CT with retries"""
    import time

    # Try weather.gov with retries
    for attempt in range(3):
        try:
            lat, lon = 41.3184, -72.3254
            points_url = f"https://api.weather.gov/points/{lat},{lon}"

            req = urllib.request.Request(
                points_url,
                headers={'User-Agent': 'BraydonMorningBriefing/1.0 (braydon@example.com)'}
            )
            with urllib.request.urlopen(req, timeout=20) as response:
                points_data = json.loads(response.read().decode('utf-8'))

            forecast_url = points_data['properties']['forecast']

            req = urllib.request.Request(
                forecast_url,
                headers={'User-Agent': 'BraydonMorningBriefing/1.0 (braydon@example.com)'}
            )
            with urllib.request.urlopen(req, timeout=20) as response:
                forecast_data = json.loads(response.read().decode('utf-8'))

            periods = forecast_data['properties']['periods']

            lines = []
            for i, period in enumerate(periods[:4]):
                name = period['name']
                temp = period['temperature']
                unit = period['temperatureUnit']
                short = period['shortForecast']
                wind = period.get('windSpeed', '')
                wind_dir = period.get('windDirection', '')

                if i == 0:
                    lines.append(f"{name}: {temp}°{unit}, {short}, Wind {wind_dir} {wind}")
                else:
                    lines.append(f"{name}: {temp}°{unit}, {short}")

            return '\n'.join(lines)

        except Exception as e:
            print(f"Warning: weather.gov attempt {attempt + 1}/3 failed: {e}", file=sys.stderr)
            if attempt < 2:
                time.sleep(2)  # Wait 2 seconds before retry

    # Fallback to wttr.in with retries
    for attempt in range(2):
        try:
            url = "https://wttr.in/Old+Lyme,CT?format=%l:+%C+%t+%w"
            with urllib.request.urlopen(url, timeout=15) as response:
                return response.read().decode('utf-8').strip()
        except Exception as e:
            print(f"Warning: wttr.in attempt {attempt + 1}/2 failed: {e}", file=sys.stderr)
            if attempt < 1:
                time.sleep(2)

    return "Weather data unavailable"


def run_perplexity_query(query: str) -> str:
    """Run a pure Perplexity query (fallback for sections without RSS)"""
    if not PP_CLI:
        return ""

    try:
        result = subprocess.run(
            [PP_CLI, '--no-interactive', query, '--output', 'markdown'],
            capture_output=True,
            text=True,
            timeout=90
        )

        if result.returncode != 0:
            return ""

        lines = result.stdout.split('\n')
        content = '\n'.join(
            line for line in lines
            if not line.startswith(('- ', 'Searching', 'Thinking'))
        )

        if '## Sources' in content:
            content = content.split('## Sources')[0]

        return content.strip()

    except Exception as e:
        print(f"Perplexity query error: {e}", file=sys.stderr)
        return ""


def process_section_with_rss(section_name: str) -> str:
    """
    Process a section using RSS feeds + LLM summarization.
    Returns summary content only (no augmentation - that's handled by deep dives).
    """
    config = get_section_config(section_name)
    if not config:
        return ""

    print(f"  Fetching RSS feeds for {section_name}...")

    # Fetch RSS items
    items = fetch_section_feeds(section_name)
    if not items:
        print(f"  No RSS items found for {section_name}", file=sys.stderr)
        return ""

    print(f"  Got {len(items)} items, processing with LLM...")

    # Format for LLM
    content_for_llm = format_items_for_llm(items)

    # Process through LLM (no augmentation - deep dives handle that)
    summary, _ = process_rss_content(
        content=content_for_llm,
        summary_prompt=config.summary_prompt or "Summarize these items as bullet points.",
        use_perplexity=False,  # No augmentation here
        use_deepseek=config.use_llm_summary,
        use_claude=False,
        augment_prompt=None,
    )

    return summary


def parse_queries_file(file_path: str) -> list[tuple[str, str]]:
    """Parse the day-specific queries file for fallback sections"""
    queries = []
    current_section = None
    current_query = []

    with open(file_path, 'r') as f:
        for line in f:
            line = line.rstrip()
            if line.startswith('SECTION:'):
                if current_section and current_query:
                    queries.append((current_section, '\n'.join(current_query)))
                current_section = line.split(':', 1)[1].strip()
                current_query = []
            elif current_section and line:
                current_query.append(line)

        if current_section and current_query:
            queries.append((current_section, '\n'.join(current_query)))

    return queries


def main():
    script_dir = Path(__file__).parent
    today = datetime.now().strftime('%Y-%m-%d')
    briefing_date = datetime.now().strftime('%A, %B %d, %Y')
    day_of_week = datetime.now().strftime('%A').lower()

    vault_path = Path('/Users/braydon/Obsidian/Bvault/Daily notes') / f'{today}.md'
    queries_file = script_dir / 'prompts' / f'{day_of_week}-queries.md'

    print(f"Generating RSS briefing for {briefing_date}...")

    # Get weather
    print("  Fetching weather...")
    weather_content = get_weather()

    results = []

    # Core daily sections (appear every day)
    core_sections = [
        "Key Headlines",
        "Connecticut",
        "Science Roundup",
    ]

    # Process core sections
    for section_name in core_sections:
        if section_name in SECTION_FEEDS:
            print(f"\nProcessing core section: {section_name}")
            content = process_section_with_rss(section_name)
            if content:
                results.append((section_name, content))

    # Get today's deep dive topics from schedule
    deep_dive_topics = DEEP_DIVE_SCHEDULE.get(day_of_week, [])

    # Process deep dives using Perplexity
    for topic in deep_dive_topics:
        if topic in DEEP_DIVE_PROMPTS:
            print(f"\nProcessing deep dive: {topic}")
            content = run_perplexity_query(DEEP_DIVE_PROMPTS[topic])
            if content:
                results.append((topic, content))

    # Process interest-based sections that have RSS feeds
    interest_sections = [
        "Tech & AI",
        "Hacker News Top Stories",
        "Classical Music",
        "Automotive",
        "Politics",
        "Archaeological Discoveries",
        "Design Innovations",
        "Cognitive Science",
    ]

    for section_name in interest_sections:
        if section_name in SECTION_FEEDS:
            print(f"\nProcessing: {section_name}")
            content = process_section_with_rss(section_name)
            if content:
                results.append((section_name, content))

    # Check for day-specific sections from legacy query files
    if queries_file.exists():
        day_queries = parse_queries_file(str(queries_file))
        for section_name, query in day_queries:
            # Skip if we already have RSS coverage or deep dive for this
            if get_section_config(section_name) or section_name in deep_dive_topics:
                continue
            # Skip weather
            if 'weather' in section_name.lower():
                continue

            print(f"\nProcessing (legacy query): {section_name}")
            content = run_perplexity_query(query)
            if content:
                results.append((section_name, content))

    # Build briefing content
    print("\nAppending to daily note...")
    vault_path.parent.mkdir(parents=True, exist_ok=True)

    briefing_content = []
    briefing_content.append('\n---\n')
    briefing_content.append(f'## Morning Briefing - {briefing_date}\n\n')

    if weather_content:
        briefing_content.append(f'**Weather** (Old Lyme, CT):\n{weather_content}\n\n')

    for section_name, content in results:
        briefing_content.append(f'### {section_name}\n\n')
        briefing_content.append(f'{content}\n\n')

    # Write to daily note
    if vault_path.exists():
        with open(vault_path, 'a') as f:
            f.write(''.join(briefing_content))
    else:
        with open(vault_path, 'w') as f:
            f.write('---\n')
            f.write('tags:\n')
            f.write('  - daily\n')
            f.write('---\n')
            f.write(''.join(briefing_content))

    print(f"✓ Briefing appended to: Daily notes/{today}.md")


if __name__ == '__main__':
    main()
