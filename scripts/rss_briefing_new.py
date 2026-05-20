#!/Users/braydon/projects/experiments/pp/scripts/venv/bin/python3

# ABOUTME: RSS-powered morning briefing with unified section scheduling
# ABOUTME: Uses day-of-week rotation to deliver 4-7 sections per day

import subprocess
import sys
import os
import urllib.request
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

# Local imports
from rss_config_new import get_sections_for_day, get_section_by_name, Section
from rss_parser import fetch_section_feeds, format_items_for_llm
from llm_processor import (
    process_rss_content,
    PP_CLI,
    PP_CLI_ERROR,
    PP_CLI_TIMEOUT_SECONDS,
)


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
    """Run a Perplexity query for deep dive topics"""
    if not PP_CLI:
        print(f"Error: {PP_CLI_ERROR}", file=sys.stderr)
        return ""

    try:
        result = subprocess.run(
            [PP_CLI, '--no-interactive', query, '--output', 'markdown'],
            capture_output=True,
            text=True,
            timeout=PP_CLI_TIMEOUT_SECONDS
        )

        if result.returncode != 0:
            return ""

        lines = result.stdout.split('\n')
        content = '\n'.join(
            line for line in lines
            if not line.startswith(('- ', 'Searching', 'Thinking'))
        )

        # Keep sources section - citations are valuable!
        return content.strip()

    except subprocess.TimeoutExpired:
        print(f"Perplexity query timed out after {PP_CLI_TIMEOUT_SECONDS:.0f}s", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"Perplexity query error: {e}", file=sys.stderr)
        return ""


def process_rss_section(section: Section) -> str:
    """
    Process an RSS-based section using feeds + LLM summarization.
    """
    print(f"  Fetching RSS feeds for {section.name}...")

    # Fetch RSS items - create a temporary SectionConfig for compatibility
    from rss_config_new import FeedSource
    from dataclasses import dataclass
    from typing import Optional

    @dataclass
    class SectionConfig:
        feeds: list[FeedSource]
        use_llm_summary: bool = True
        use_perplexity_augment: bool = False
        summary_prompt: Optional[str] = None
        max_items: int = 5

    # Create temporary config
    temp_config = SectionConfig(
        feeds=section.feeds,
        use_llm_summary=True,
        use_perplexity_augment=False,
        summary_prompt=section.summary_prompt,
        max_items=section.max_items
    )

    # Fetch items using existing parser
    # We need to create a dict entry for the parser
    temp_feeds = {section.name: temp_config}

    # Manually fetch and process
    from rss_parser import fetch_feed, deduplicate_items

    all_items = []
    for feed in section.feeds:
        items = fetch_feed(feed)
        all_items.extend(items)

    # Deduplicate and sort
    items = deduplicate_items(all_items)
    items = items[:section.max_items]

    if not items:
        print(f"  No RSS items found for {section.name}", file=sys.stderr)
        return ""

    print(f"  Got {len(items)} items, processing with LLM...")

    # Format for LLM
    content_for_llm = format_items_for_llm(items)

    # Process through LLM
    summary, _ = process_rss_content(
        content=content_for_llm,
        summary_prompt=section.summary_prompt or "Summarize these items as bullet points.",
        use_perplexity=False,
        use_deepseek=True,
        use_claude=False,
        augment_prompt=None,
    )

    return summary


def main():
    script_dir = Path(__file__).parent
    today = datetime.now().strftime('%Y-%m-%d')
    briefing_date = datetime.now().strftime('%A, %B %d, %Y')
    day_of_week = datetime.now().strftime('%A').lower()

    vault_path = Path('/Users/braydon/Obsidian/Bvault/Daily notes') / f'{today}.md'

    print(f"Generating briefing for {briefing_date}...")

    # Get weather
    print("  Fetching weather...")
    weather_content = get_weather()

    # Get sections scheduled for today
    sections = get_sections_for_day(day_of_week)

    print(f"\nScheduled sections for {day_of_week}: {len(sections)}")
    for section in sections:
        print(f"  - {section.name} ({section.type})")

    needs_perplexity = any(section.type == "perplexity" for section in sections)
    if needs_perplexity and not PP_CLI:
        print(f"Error: {PP_CLI_ERROR}", file=sys.stderr)
        sys.exit(2)

    results = []

    # Process each scheduled section
    for section in sections:
        print(f"\nProcessing: {section.name} ({section.type})")

        if section.type == "rss":
            content = process_rss_section(section)
            if content:
                results.append((section.name, content))

        elif section.type == "perplexity":
            content = run_perplexity_query(section.search_prompt)
            if content:
                results.append((section.name, content))

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
    print(f"✓ Total sections: {len(results) + 1} (Weather + {len(results)} sections)")


if __name__ == '__main__':
    main()
