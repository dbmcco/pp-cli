#!/bin/bash

# ABOUTME: Multi-query morning briefing - runs separate queries per section

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get today's date
TODAY=$(date +"%Y-%m-%d")
BRIEFING_DATE=$(date +"%A, %B %d, %Y")
DAY_OF_WEEK=$(date +"%A" | tr '[:upper:]' '[:lower:]')

# Output file in vault
VAULT_PATH="/Users/braydon/Obsidian/Bvault/daily-briefings/${TODAY}-news-briefing.md"
TEMP_DIR="/tmp/pp-briefing-$$"

# Select the queries file
QUERIES_FILE="${SCRIPT_DIR}/prompts/${DAY_OF_WEEK}-queries.md"

# Check if queries file exists
if [ ! -f "$QUERIES_FILE" ]; then
  echo "Error: Queries file not found: $QUERIES_FILE"
  exit 1
fi

# Create temp directory
mkdir -p "$TEMP_DIR"

# Parse the queries file and run each section
echo "Generating briefing for ${BRIEFING_DATE}..."

# Extract sections and queries
awk '/^SECTION:/ {
  if (section) print query
  section = $2
  query = ""
  next
}
{
  if (section) {
    if (query) query = query "\n" $0
    else query = $0
  }
}
END {
  if (section && query) print query
}' "$QUERIES_FILE" | while IFS= read -r query; do
  # Get the section name from the previous SECTION: line
  section=$(grep -B1 "^${query:0:50}" "$QUERIES_FILE" | grep "^SECTION:" | cut -d: -f2 | xargs)

  if [ -n "$section" ]; then
    echo "  Querying: $section..."

    # Run query and save to temp file
    section_file="$TEMP_DIR/${section// /_}.txt"
    pp --no-interactive "$query" --output markdown 2>/dev/null | grep -v "^Searching..." | grep -v "^Thinking" > "$section_file"
  fi
done

# Actually parse correctly using awk
current_section=""
current_query=""

while IFS= read -r line; do
  if [[ "$line" =~ ^SECTION:\ (.+)$ ]]; then
    # Save previous section if exists
    if [ -n "$current_section" ] && [ -n "$current_query" ]; then
      echo "  Querying: $current_section..."
      section_file="$TEMP_DIR/${current_section// /_}.txt"
      pp --no-interactive "$current_query" --output markdown 2>/dev/null | grep -v "^- " > "$section_file"
    fi

    # Start new section
    current_section="${BASH_REMATCH[1]}"
    current_query=""
  elif [ -n "$current_section" ] && [ -n "$line" ]; then
    # Append to current query
    if [ -n "$current_query" ]; then
      current_query="${current_query}\n${line}"
    else
      current_query="$line"
    fi
  fi
done < "$QUERIES_FILE"

# Don't forget the last section
if [ -n "$current_section" ] && [ -n "$current_query" ]; then
  echo "  Querying: $current_section..."
  section_file="$TEMP_DIR/${current_section// /_}.txt"
  echo -e "$current_query" | pp --no-interactive "$(cat)" --output markdown 2>/dev/null | grep -v "^- " > "$section_file"
fi

# Combine all sections into final note
echo "Combining sections..."

cat > "$VAULT_PATH" << EOF
---
created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
query: "Morning Briefing"
tags: [briefing, daily, perplexity]
---

# Morning Briefing - ${BRIEFING_DATE}

EOF

# Add each section
for section_file in "$TEMP_DIR"/*.txt; do
  if [ -f "$section_file" ]; then
    section_name=$(basename "$section_file" .txt | tr '_' ' ')
    echo "## $section_name" >> "$VAULT_PATH"
    echo "" >> "$VAULT_PATH"
    cat "$section_file" >> "$VAULT_PATH"
    echo "" >> "$VAULT_PATH"
    echo "" >> "$VAULT_PATH"
  fi
done

# Cleanup
rm -rf "$TEMP_DIR"

echo "✓ Briefing saved to: daily-briefings/${TODAY}-news-briefing.md"
