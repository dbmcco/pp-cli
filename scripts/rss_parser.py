#!/Users/braydon/projects/experiments/pp/scripts/venv/bin/python3

# ABOUTME: RSS feed parser for morning briefing
# ABOUTME: Fetches, parses, and deduplicates items from multiple RSS sources

import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from html import unescape
import re

try:
    import feedparser
except ImportError:
    print("Error: feedparser not installed. Run: pip install feedparser", file=sys.stderr)
    sys.exit(1)

from rss_config import FeedSource, SectionConfig, get_section_config


@dataclass
class FeedItem:
    """Parsed RSS feed item"""
    title: str
    link: str
    summary: str
    source: str
    published: Optional[datetime]
    priority: int  # From feed source


def clean_html(text: str) -> str:
    """Remove HTML tags and decode entities"""
    if not text:
        return ""
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    clean = unescape(clean)
    # Normalize whitespace
    clean = ' '.join(clean.split())
    return clean.strip()


def parse_date(entry: dict) -> Optional[datetime]:
    """Extract publication date from feed entry"""
    # Try common date fields
    for field in ['published_parsed', 'updated_parsed', 'created_parsed']:
        if field in entry and entry[field]:
            try:
                return datetime(*entry[field][:6])
            except (TypeError, ValueError):
                continue
    return None


def fetch_feed(source: FeedSource, max_age_hours: int = 48) -> list[FeedItem]:
    """Fetch and parse a single RSS feed"""
    items = []
    cutoff = datetime.now() - timedelta(hours=max_age_hours)

    try:
        feed = feedparser.parse(source.url)

        if feed.bozo and not feed.entries:
            print(f"  Warning: Failed to parse {source.name}: {feed.bozo_exception}", file=sys.stderr)
            return items

        for entry in feed.entries[:source.max_items]:
            title = clean_html(entry.get('title', ''))
            if not title:
                continue

            # Get summary/description
            summary = ''
            if 'summary' in entry:
                summary = clean_html(entry.summary)
            elif 'description' in entry:
                summary = clean_html(entry.description)

            # Truncate long summaries
            if len(summary) > 300:
                summary = summary[:297] + '...'

            # Get link
            link = entry.get('link', '')

            # Get date
            published = parse_date(entry)

            # Filter by age if we have a date
            if published and published < cutoff:
                continue

            items.append(FeedItem(
                title=title,
                link=link,
                summary=summary,
                source=source.name,
                published=published,
                priority=source.priority,
            ))

    except Exception as e:
        print(f"  Error fetching {source.name}: {e}", file=sys.stderr)

    return items


def deduplicate_items(items: list[FeedItem]) -> list[FeedItem]:
    """Remove duplicate items based on title similarity"""
    seen_titles = set()
    unique_items = []

    for item in items:
        # Normalize title for comparison
        normalized = item.title.lower()
        # Remove common prefixes/suffixes
        normalized = re.sub(r'^(breaking|update|watch|live):\s*', '', normalized)
        normalized = re.sub(r'\s*\|.*$', '', normalized)  # Remove "| Source" suffixes

        # Simple similarity check - first 50 chars
        key = normalized[:50]

        if key not in seen_titles:
            seen_titles.add(key)
            unique_items.append(item)

    return unique_items


def fetch_section_feeds(section_name: str, max_age_hours: int = 48) -> list[FeedItem]:
    """Fetch all feeds for a section and return deduplicated items"""
    config = get_section_config(section_name)
    if not config:
        print(f"  No RSS config for section: {section_name}", file=sys.stderr)
        return []

    all_items = []
    for source in config.feeds:
        print(f"    Fetching {source.name}...", file=sys.stderr)
        items = fetch_feed(source, max_age_hours)
        all_items.extend(items)
        print(f"    Got {len(items)} items from {source.name}", file=sys.stderr)

    # Sort by priority (lower first), then by date (newest first)
    all_items.sort(key=lambda x: (x.priority, -(x.published.timestamp() if x.published else 0)))

    # Deduplicate
    unique_items = deduplicate_items(all_items)

    # Limit to max items
    return unique_items[:config.max_items * 2]  # Return extra for LLM to filter


def format_items_for_llm(items: list[FeedItem]) -> str:
    """Format feed items as text for LLM processing"""
    lines = []
    for i, item in enumerate(items, 1):
        date_str = item.published.strftime('%Y-%m-%d %H:%M') if item.published else 'unknown date'
        lines.append(f"{i}. [{item.source}] {item.title}")
        if item.summary:
            lines.append(f"   Summary: {item.summary}")
        lines.append(f"   Link: {item.link}")
        lines.append(f"   Date: {date_str}")
        lines.append("")
    return '\n'.join(lines)


def format_items_as_markdown(items: list[FeedItem], max_items: int = 5) -> str:
    """Format feed items directly as markdown bullets"""
    lines = []
    for item in items[:max_items]:
        lines.append(f"• **{item.title}**: {item.summary} [{item.source}]({item.link})")
    return '\n'.join(lines)


# Quick test
if __name__ == '__main__':
    print("Testing RSS parser...")
    items = fetch_section_feeds("Key Headlines")
    print(f"\nGot {len(items)} items for Key Headlines:\n")
    print(format_items_for_llm(items[:5]))
