# Morning Briefing System - Current Architecture Analysis

**Date:** 2025-12-10  
**Analysis Scope:** Complete data flow from RSS feeds → LLM processing → Obsidian output

---

## Executive Summary

The morning briefing system is a **hybrid RSS + LLM architecture** that pulls from curated RSS feeds, processes them through DeepSeek/Perplexity for summarization, and appends results to Obsidian daily notes. However, there are two fundamentally different execution paths:

1. **RSS-First Path** (`rss_briefing.py`) - Primary, newer approach using RSS feeds for core sections + Perplexity for deep dives
2. **Query-First Path** (`multi-query-briefing.py`) - Legacy approach using Perplexity CLI directly for all content

The system currently **produces 15-20 sections per day** (target: 4-6) due to both paths running interest-based sections every single day, which is why you're seeing repetition and mystery sections.

---

## Data Flow Architecture

### Entry Point: `rss_briefing.py` (Primary)

```
START: Daily Cron/Manual Invocation
  ↓
Get Weather (weather.gov API with retries)
  ↓
CORE SECTIONS (Always run - 3 sections):
  ├── Key Headlines (RSS)
  ├── Connecticut (RSS)
  └── Science Roundup (RSS)
  ↓
DEEP DIVE TOPICS (Rotate by day):
  └── 1-3 topics from DEEP_DIVE_SCHEDULE (Perplexity web search)
  ↓
INTEREST SECTIONS (Always run - 8 sections):
  ├── Tech & AI (RSS)
  ├── Hacker News Top Stories (RSS)
  ├── Classical Music (RSS)
  ├── Automotive (RSS)
  ├── Politics (RSS)
  ├── Archaeological Discoveries (RSS)
  ├── Design Innovations (RSS)
  └── Cognitive Science (RSS)
  ↓
LEGACY FALLBACK:
  └── Parse day-specific queries file for additional sections
  ↓
WRITE TO OBSIDIAN:
  └── /Users/braydon/Obsidian/Bvault/Daily notes/{YYYY-MM-DD}.md
```

---

## Component Map

### 1. Configuration Layer (`rss_config.py`)

**Responsibility:** Define all RSS sources, scheduling, and processing prompts

#### Data Structures
```python
FeedSource(name, url, priority, max_items)
  └─ Individual RSS feed metadata

SectionConfig(feeds[], use_llm_summary, use_perplexity_augment, summary_prompt, max_items)
  └─ Complete configuration for a briefing section
```

#### Key Configuration Maps

**SECTION_FEEDS** (Lines 29-245)
- 11 sections defined, each with curated RSS sources
- EVERY section has `use_llm_summary=True` by default
- NO augmentation enabled (Deep dives handle that)

| Section | Sources | Use LLM | Daily? |
|---------|---------|--------|---------|
| Key Headlines | Google News, NPR, BBC | Yes | YES (Core) |
| Connecticut | CT Mirror, Hartford Courant, CT News Junkie | Yes | YES (Core) |
| Science Roundup | Nature News, Science News, Phys.org | Yes | YES (Core) |
| Tech & AI | Hacker News, Ars Technica, The Verge, TechCrunch | Yes | YES (Interest) |
| Hacker News Top Stories | Hacker News | Yes | YES (Interest) |
| Classical Music | Slipped Disc, Gramophone | Yes | YES (Interest) |
| Automotive | Car and Driver, Jalopnik | Yes | YES (Interest) |
| Politics | NPR Politics, Google News Politics | Yes | YES (Interest) |
| Archaeological Discoveries | Archaeology.org, Heritage Daily | Yes | YES (Interest) |
| Design Innovations | Core77, Dezeen | Yes | YES (Interest) |
| Cognitive Science | Psychology Today, ScienceDaily Neuroscience | Yes | YES (Interest) |

**DEEP_DIVE_SCHEDULE** (Lines 249-257)
- 7 topics per week, 1-3 per day, rotates by day of week
- Each topic gets its own Perplexity web search query

| Day | Topics | Purpose |
|-----|--------|---------|
| Monday | Contemporary Music Trends, AI Workflows & Tools, Design Innovations | Week planning + interests |
| Tuesday | Archaeological Discoveries, Cognitive Science Research, EV & Autonomous Tech | Interests focus |
| Wednesday | New Music Compositions, AI System Architecture, Intellectual Trends | Music + technical depth |
| Thursday | Materials Science & Manufacturing, Design Principles, Automotive Releases | Design + automotive |
| Friday | Week in Review | Synthesis + planning weekend |
| Saturday | Cultural Events, Race Calendar | Local activities |
| Sunday | Cultural Events, Race Calendar | Local activities |

**DEEP_DIVE_PROMPTS** (Lines 260-413)
- Perplexity-specific search queries with detailed instructions
- 15 different deep dive prompts available
- Focus on web search capability (Perplexity's strength)

---

### 2. Orchestration Layer (`rss_briefing.py`)

**Responsibility:** Coordinate RSS fetching, LLM processing, and Obsidian output

#### Main Function Flow (Lines 176-282)

**Step 1: Setup** (Lines 177-184)
```python
- Get today's date and day of week
- Determine vault path: /Users/braydon/Obsidian/Bvault/Daily notes/{YYYY-MM-DD}.md
- Locate day-specific queries file: prompts/{day_of_week}-queries.md
```

**Step 2: Weather** (Lines 187-189)
```python
get_weather() → weather.gov with fallback to wttr.in
```

**Step 3: Core Sections** (Lines 194-206)
```python
ALWAYS process:
  - Key Headlines
  - Connecticut
  - Science Roundup
```

**Step 4: Deep Dives** (Lines 208-217)
```python
Get topics from DEEP_DIVE_SCHEDULE[day_of_week]
For each topic:
  - Look up prompt in DEEP_DIVE_PROMPTS
  - Run Perplexity query (web search)
  - Append result
```

**Step 5: Interest Sections** (Lines 219-236)
```python
ALWAYS process 8 sections:
  - Tech & AI
  - Hacker News Top Stories
  - Classical Music
  - Automotive
  - Politics
  - Archaeological Discoveries
  - Design Innovations
  - Cognitive Science
```

**Step 6: Legacy Fallback** (Lines 238-252)
```python
If {day_of_week}-queries.md exists:
  Parse queries
  Skip sections already covered by RSS or deep dives
  Run remaining Perplexity queries
```

**Step 7: Write Output** (Lines 254-279)
```python
Format markdown:
  ## Morning Briefing - {formatted_date}
  
  **Weather**: ...
  
  ### {Section 1}
  ...
  
  ### {Section 2}
  ...
```

#### Key Functions

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `process_section_with_rss()` | Fetch RSS + LLM summarize | section_name | summary string |
| `run_perplexity_query()` | Pure Perplexity web search | query string | web search result |
| `parse_queries_file()` | Parse legacy queries | file path | list[(section, query)] |
| `get_weather()` | Fetch weather with retries | none | weather string |

---

### 3. Data Fetching Layer (`rss_parser.py`)

**Responsibility:** Fetch, parse, deduplicate RSS feeds

#### Processing Pipeline
```python
FeedSource → feedparser → FeedItem[] → Deduplicate → Sort → Return
```

#### Key Functions

| Function | Purpose | Details |
|----------|---------|---------|
| `fetch_feed()` | Single RSS source | - Parses with feedparser<br/>- Cleans HTML<br/>- Filters by age (48h default)<br/>- Max 10 items per source |
| `fetch_section_feeds()` | All feeds for section | - Calls fetch_feed() for each source<br/>- Sorts by priority + date<br/>- Deduplicates by title similarity<br/>- Returns 2x max_items (for LLM filtering) |
| `deduplicate_items()` | Remove near-duplicates | - Title normalization<br/>- First 50 chars comparison<br/>- Removes prefixes like "Breaking:" |
| `format_items_for_llm()` | Feed items → LLM input | Structured text with [Source], summary, link, date |
| `format_items_as_markdown()` | Feed items → bullets | Direct markdown bullets |

#### FeedItem Structure (Lines 22-30)
```python
@dataclass
class FeedItem:
    title: str              # Article headline
    link: str               # URL to article
    summary: str            # First 300 chars
    source: str             # Feed source name
    published: Optional[datetime]  # Parse date from feed
    priority: int           # From FeedSource priority
```

---

### 4. LLM Processing Layer (`llm_processor.py`)

**Responsibility:** Interface with LLM backends (DeepSeek, Claude, Perplexity)

#### Three LLM Backends Supported

| Backend | Function | Capability | Use Case |
|---------|----------|-----------|----------|
| **DeepSeek** | `summarize_with_deepseek()` | Summarizes provided content | Primary RSS summarization |
| **Claude** | `summarize_with_claude()` | Summarizes provided content | Fallback RSS summarization |
| **Perplexity** | `summarize_with_perplexity()` | Web search + synthesis | Deep dives + augmentation |

#### Processing Pipeline for RSS Content

```python
process_rss_content(content, prompt, use_deepseek, use_claude, augment_prompt)
  ↓
STEP 1: Summarization (try in order)
  ├─ If use_deepseek=True && DEEPSEEK_API_KEY: DeepSeek (primary)
  ├─ Else if use_claude=True && ANTHROPIC_API_KEY: Claude
  └─ Else: format_rss_as_bullets() (fallback)
  ↓
STEP 2: Optional Augmentation (if augment_prompt provided)
  └─ Perplexity web search for additional context
  ↓
RETURN: (summary, augmentation) tuple
```

#### Key Functions

| Function | Input | Output | Notes |
|----------|-------|--------|-------|
| `summarize_with_deepseek()` | content, prompt, model | str | Cost-effective, used for RSS |
| `summarize_with_claude()` | content, prompt, model | str | Backup RSS summarizer |
| `summarize_with_perplexity()` | content, prompt | str | Web search, used for deep dives |
| `augment_with_perplexity()` | headlines, augment_prompt | str | Add context via web search |
| `format_rss_as_bullets()` | content, max_items | str | Fallback when no LLM available |

#### Environment Requirements
```python
PP_CLI_PATH          # Path to Perplexity CLI (default: /opt/homebrew/bin/pp)
DEEPSEEK_API_KEY     # For summarization
ANTHROPIC_API_KEY    # For Claude fallback
```

---

### 5. Legacy Path (`multi-query-briefing.py`)

**Responsibility:** Alternative all-Perplexity approach (NOT currently used)

**Key Differences from rss_briefing.py:**
- Uses Perplexity for ALL content (no RSS feeds)
- Extracts and renumbers citations from Perplexity responses
- Collects all citations into unified References section
- Preserves source URLs

**When Used:** This script exists as an alternative but `rss_briefing.py` is the current primary implementation.

**Citation Preservation:** Multi-query-briefing has robust citation handling that rss_briefing.py lacks:
```python
1. Extract citations from "## Sources" section
2. Build global citation map (renumber across sections)
3. Renumber [N] references in content
4. Append unified References section at end
```

---

## Section Selection Mechanism

### How Sections Are Determined

```
Daily Execution Order:

1. WEATHER (Always)
   → get_weather() → weather.gov with retries

2. CORE (Always - 3 sections)
   → "Key Headlines", "Connecticut", "Science Roundup"
   → Each checked in SECTION_FEEDS
   → process_section_with_rss() called

3. DEEP DIVES (1-3 per day - Rotates)
   → DEEP_DIVE_SCHEDULE[day_of_week] → list of topics
   → DEEP_DIVE_PROMPTS[topic] → Perplexity query
   → run_perplexity_query() called

4. INTEREST (Always - 8 sections)
   → Hardcoded list: Tech & AI, Hacker News, Music, etc.
   → Each checked in SECTION_FEEDS
   → process_section_with_rss() called

5. LEGACY FALLBACK (Conditional)
   → IF {day_of_week}-queries.md exists
   → Parse SECTION: ... format
   → Skip already-processed sections
   → Run remaining as Perplexity queries
```

### Why You Get 15-20 Sections

**Math:**
- Weather: 1
- Core sections: 3
- Deep dives: 1-3 per day
- Interest sections: 8 (ALWAYS)
- Legacy fallback: 0-5 (if queries file exists)

**Total: 13-19 sections per day**

This is the **primary architectural problem**. The interest sections are hardcoded to run every single day, creating the volume and repetition issues you noted.

---

## Mystery Sections Investigation

### Potential Sources of Unexpected Sections

**Scenario 1: Legacy Queries File Overrides**
- File: `scripts/prompts/{day_of_week}-queries.md`
- If a section_name in queries file does NOT exist in SECTION_FEEDS
- And it's NOT in DEEP_DIVE_SCHEDULE
- It gets processed as a Perplexity query (Lines 238-252)

**Scenario 2: Fuzzy Matching in get_section_config()**
```python
def get_section_config(section_name: str) -> Optional[SectionConfig]:
    # Exact match first
    if section_name in SECTION_FEEDS:
        return SECTION_FEEDS[section_name]
    
    # Fuzzy match - case-insensitive, partial
    section_lower = section_name.lower()
    for key, config in SECTION_FEEDS.items():
        if key.lower() in section_lower or section_lower in key.lower():
            return config
    
    return None
```

**Example:** A query section called "Classical & Contemporary Music" could match "Classical Music" via fuzzy matching.

### Checking for Mystery Sections

To identify which sections are appearing in output but NOT defined in rss_config.py:

1. Run the briefing
2. Extract all section names from Obsidian output
3. Cross-reference against:
   - `SECTION_FEEDS.keys()` (11 sections)
   - `DEEP_DIVE_SCHEDULE[day_of_week]` (1-3 sections)
   - `{day_of_week}-queries.md` parsed sections
4. Any mismatch = mystery section

**Most likely source:** Legacy queries files (Lines 238-252 in rss_briefing.py) combined with fuzzy matching that creates unexpected sections.

---

## Data Flow for Citations

### Current State: BROKEN

**RSS Feed Path:**
```
FeedItem (has link) → format_items_for_llm()
→ LLM prompt says "Format with source attribution"
→ DeepSeek summarizes but LOSES the link
→ format_rss_as_bullets() fallback ALSO loses links
→ Result: No clickable citations in output
```

**Deep Dive Path:**
```
run_perplexity_query() → Perplexity returns "## Sources" section
→ Line 109: content.split('## Sources')[0]  ← STRIP SOURCES
→ Result: Web search citations DISCARDED
```

### How It Should Work (multi-query-briefing.py approach)

```
1. Extract from "## Sources" section with regex
2. Build list: [(domain, url), ...]
3. Renumber citations in content: [1], [2], etc.
4. Append unified References section:
   1. [domain.com](url)
   2. [other.com](other_url)
```

### Why Citations Are Missing

**Root Cause:** rss_briefing.py was designed to simplify the system by:
- Removing Perplexity's "## Sources" (line 108-109)
- Letting RSS feed item links carry citations instead
- But DeepSeek never includes links in summaries

**Fix Required:** Add citation preservation to LLM summarization prompts and output parsing.

---

## Processing Stages & LLM Choices

### Stage 1: RSS Fetching (No LLM)
```
RSS Source → feedparser → Deduplicate → Return FeedItem[]
Time: 2-5 seconds per section
```

### Stage 2: RSS Summarization (DeepSeek)
```
FeedItem[] → format_items_for_llm() → DeepSeek API
Prompt: Custom summary_prompt from SECTION_FEEDS[section].summary_prompt
Cost: ~$0.01 per section
Time: 10-30 seconds per section
```

**Example Prompts:**
- Key Headlines: "Select 3-5 most important global news stories"
- Tech & AI: "Identify 3-5 most significant stories for systems builders"
- Classical Music: "Select notable stories focusing on contemporary composers"

### Stage 3: Deep Dives (Perplexity)
```
DEEP_DIVE_PROMPTS[topic] → Perplexity CLI --no-interactive
Capability: Web search + synthesis
Cost: ~$0.05 per query (based on token usage)
Time: 20-60 seconds per deep dive
```

**Example Prompts:**
- "Search for current trends in contemporary classical music composition"
- "Search for new CLI tools, frameworks, and integration patterns for AI"
- "Search for upcoming events in next 2 weeks within 50 miles of Old Lyme, CT"

### Stage 4: Legacy Fallback (Perplexity)
```
IF queries file exists AND section not yet processed:
  Parse section query → Perplexity CLI web search
```

### Stage 5: Output (No LLM)
```
Build markdown → Append to Obsidian daily note
```

---

## Code Paths & Execution Order

### Path A: Section Has RSS (ALWAYS TAKEN FIRST)

```python
# Lines 201-206 (Core sections)
# Lines 231-236 (Interest sections)

section_name in SECTION_FEEDS → get_section_config() → process_section_with_rss()
  ↓
process_rss_content(
  content=format_items_for_llm(items),
  summary_prompt=config.summary_prompt,
  use_perplexity=False,           ← NO augmentation
  use_deepseek=config.use_llm_summary,
  use_claude=False,
  augment_prompt=None,
)
```

### Path B: Deep Dive Topics

```python
# Lines 208-217

topic in DEEP_DIVE_SCHEDULE[day_of_week] → run_perplexity_query(DEEP_DIVE_PROMPTS[topic])
  ↓
Perplexity --no-interactive --output markdown
  ↓
Strip "## Sources" section
  ↓
Append to results
```

### Path C: Legacy Queries Fallback

```python
# Lines 238-252

IF queries_file.exists():
  parse_queries_file() → list[(section_name, query)]
  
  FOR (section_name, query) IN queries:
    IF section_name already processed: skip
    IF "weather" in section_name: skip
    ELSE:
      run_perplexity_query(query) → append to results
```

---

## What Runs Every Day vs. What Rotates

### DAILY (Same every day - 11 sections)
```
Weather (1)
├─ weather.gov + wttr.in API
├─ Takes 30-60 seconds with retries

Core Sections (3)
├─ Key Headlines (Google News, NPR, BBC)
├─ Connecticut (CT Mirror, Hartford Courant)
├─ Science Roundup (Nature, Science News, Phys.org)

Interest Sections (8)
├─ Tech & AI
├─ Hacker News Top Stories
├─ Classical Music
├─ Automotive
├─ Politics
├─ Archaeological Discoveries
├─ Design Innovations
└─ Cognitive Science
```

### ROTATING (Varies by day of week - 1-3 sections)
```
Monday:    Contemporary Music Trends, AI Workflows & Tools, Design Innovations (3)
Tuesday:   Archaeological Discoveries, Cognitive Science Research, EV & Autonomous (3)
Wednesday: New Music Compositions, AI System Architecture, Intellectual Trends (3)
Thursday:  Materials Science & Manufacturing, Design Principles, Automotive Releases (3)
Friday:    Week in Review (1)
Saturday:  Cultural Events, Race Calendar (2)
Sunday:    Cultural Events, Race Calendar (2)
```

### LEGACY FALLBACK (Conditional)
```
IF {day_of_week}-queries.md exists:
  Parse and run remaining sections as Perplexity queries
  
Monday:    Week Ahead Preview, GenAI & LLMs Deep Dive, Tech Industry Moves (3)
Friday:    Weekend Culture & Entertainment, Hacker News Weekly Top (2)
(Other days: queries file exists but sections may be skipped if already processed)
```

---

## Technical Constraints & Dependencies

### Required APIs & Environment

| Component | Requirement | Fallback |
|-----------|-------------|----------|
| Weather | weather.gov (no key) | wttr.in API |
| RSS Feeds | feedparser library | (none - hard error) |
| DeepSeek | DEEPSEEK_API_KEY | None (uses format_rss_as_bullets) |
| Claude | ANTHROPIC_API_KEY | (none - fallback to format_rss_as_bullets) |
| Perplexity | PP_CLI_PATH env var or /opt/homebrew/bin/pp | No deep dives or legacy queries |
| Obsidian Output | /Users/braydon/Obsidian/Bvault/Daily notes/ | Creates directory if missing |

### Timeout Settings
```python
weather.gov API:   20 seconds per request (3 attempts total)
wttr.in API:       15 seconds per request (2 attempts)
Perplexity query:  90 seconds per query
DeepSeek API:      (default httpx timeout ~30s)
RSS fetch:         (feedparser default ~30s)
```

### Resource Limits
```python
Max items per feed:      10 (FeedSource.max_items)
Max items returned:      5 (SectionConfig.max_items) × 2 = 10 for LLM
LLM summary max tokens:  1024 (hardcoded)
RSS age filter:          48 hours (max_age_hours)
```

---

## Known Issues & Gaps

### Issue 1: Volume Problem
**Problem:** 13-19 sections per day vs. target of 4-6
**Cause:** Interest sections (8) run every single day
**Impact:** Brief is overwhelming, reduces likelihood of reading

### Issue 2: Missing Citations
**Problem:** No URLs/source attribution in summaries
**Cause:** DeepSeek doesn't include links; Perplexity sources are stripped
**Impact:** Can't follow up on interesting stories
**Evidence in Code:**
- Line 108-109: `if '## Sources' in filtered: filtered = filtered.split('## Sources')[0]`
- DeepSeek prompts don't mention "include URL" or "link to source"

### Issue 3: Meta-Summarization
**Problem:** Output contains "Based on the provided sources..." phrases
**Cause:** DeepSeek producing conversational output instead of direct content
**Impact:** Reduces scannability, adds unnecessary framing
**Solution:** Add to prompt: "Provide summaries directly as bullet points. Do NOT include phrases like 'Based on...' or explain the source material."

### Issue 4: Legacy Code Paths
**Problem:** Both rss_briefing.py and multi-query-briefing.py exist; unclear which is "correct"
**Cause:** System evolved from queries-only to RSS-hybrid approach
**Impact:** Confusion about canonical data flow
**Status:** rss_briefing.py appears to be primary (referenced in docs), but both are present

### Issue 5: Mystery Sections
**Problem:** Extra sections appearing in output not defined in rss_config.py
**Cause:** Likely legacy queries file (prompts/{day_of_week}-queries.md) being parsed
**Investigation:** Lines 238-252 of rss_briefing.py parse queries file and run sections not in RSS config
**Status:** Need to check if queries files still exist and are being used

---

## Architecture Decisions

### Design Pattern: Hybrid RSS + LLM
- **Why RSS?** Curated, authoritative sources; fast, deterministic
- **Why LLM?** Summarization, filtering, intelligent synthesis
- **Why Perplexity for deep dives?** Web search capability; can find latest trends

### Design Pattern: Daily Core + Rotating Interest
- **Daily core** (weather, headlines, CT, science) = consistent baseline
- **Rotating deep dives** = vary content, provide depth
- **Interest sections** = currently ALWAYS run (problematic)

### Design Pattern: Graceful Degradation
- If DeepSeek unavailable → format_rss_as_bullets() (line 285-287)
- If Perplexity unavailable → skip deep dives/legacy queries
- If RSS source fails → report warning, continue with other sources
- If weather API fails → use fallback wttr.in

### Design Pattern: Source Priority
```python
# Line 147-148 in rss_parser.py
all_items.sort(key=lambda x: (x.priority, -(x.published.timestamp() if x.published else 0)))
```
Lower priority number = higher ranking
Within same priority = newer articles first

---

## File Structure Reference

```
/Users/braydon/projects/experiments/pp/
├── scripts/
│   ├── rss_briefing.py           ← PRIMARY entry point
│   ├── rss_config.py             ← Configuration (SECTION_FEEDS, schedules, prompts)
│   ├── rss_parser.py             ← RSS fetching & parsing
│   ├── llm_processor.py          ← LLM backends (DeepSeek, Claude, Perplexity)
│   ├── multi-query-briefing.py   ← LEGACY alternative (all-Perplexity)
│   └── prompts/
│       ├── monday.md, tuesday.md, ...      ← Legacy prompt templates
│       ├── monday-queries.md, ...          ← Legacy queries format
│       └── (These are parsed in rss_briefing.py lines 238-252)
└── docs/
    ├── briefing-goals.md         ← Requirements & pain points
    └── plans/
```

---

## Data Structure Visualization

```
┌─ SECTION_FEEDS (dict[str, SectionConfig])
│  └─ "Key Headlines": SectionConfig
│     └─ feeds: [FeedSource, FeedSource, ...]
│        ├─ FeedSource("Google News", url, priority=1)
│        ├─ FeedSource("NPR", url, priority=2)
│        └─ FeedSource("BBC", url, priority=3)
│     └─ use_llm_summary: True
│     └─ summary_prompt: "Select 3-5 most important..."
│     └─ max_items: 5
│
├─ DEEP_DIVE_SCHEDULE (dict[str, list[str]])
│  └─ "monday": ["Contemporary Music Trends", "AI Workflows & Tools", ...]
│
├─ DEEP_DIVE_PROMPTS (dict[str, str])
│  └─ "Contemporary Music Trends": "Search for current trends..."
│
└─ Runtime: Results list[tuple[str, str]]
   ├─ ("Key Headlines", "• **Story 1**: ...")
   ├─ ("Connecticut", "• **Story 2**: ...")
   └─ ... (up to 19 tuples)
```

---

## Execution Timeline (Approximate)

```
Start: rss_briefing.py main()
├─ 0:00-0:05   Get weather (with retries)
├─ 0:05-0:20   Process Key Headlines RSS + DeepSeek
├─ 0:20-0:35   Process Connecticut RSS + DeepSeek
├─ 0:35-0:50   Process Science Roundup RSS + DeepSeek
├─ 0:50-2:30   Process 1-3 deep dives (Perplexity web search, slower)
├─ 2:30-5:30   Process 8 interest sections RSS + DeepSeek (10 processes in parallel? No, sequential)
├─ 5:30-7:00   Process legacy fallback queries (if any)
└─ 7:00-7:05   Write to Obsidian
Total: ~7-8 minutes per run
```

---

## Next Steps for Debugging

To understand the "mystery sections" and volume issues:

1. **Run the briefing** and capture full output
2. **Extract section names** from Obsidian note
3. **Compare against:**
   ```python
   # Line 194-198 (core sections)
   core = {"Key Headlines", "Connecticut", "Science Roundup"}
   
   # Lines 220-229 (interest sections)
   interest = {
       "Tech & AI", "Hacker News Top Stories", "Classical Music", "Automotive",
       "Politics", "Archaeological Discoveries", "Design Innovations", "Cognitive Science"
   }
   
   # Line 209 (deep dives for that day)
   deep_dives = DEEP_DIVE_SCHEDULE[datetime.now().strftime('%A').lower()]
   
   # Lines 239-252 (legacy fallback)
   queries_file = Path(__file__).parent / 'prompts' / f'{day_of_week}-queries.md'
   if queries_file.exists():
       # Parse sections from file
   ```
4. **For each unexpected section:** Trace which code path produced it

---

## Summary Table: Section Processing Paths

| Section | Config | Path | LLM | Time | Notes |
|---------|--------|------|-----|------|-------|
| Weather | None | API | No | 30-60s | weather.gov + fallback |
| Key Headlines | RSS | Core | DeepSeek | 10-15s | Always runs |
| Connecticut | RSS | Core | DeepSeek | 10-15s | Always runs |
| Science Roundup | RSS | Core | DeepSeek | 10-15s | Always runs |
| Monday: Contemporary Music | Prompt | Deep Dive | Perplexity | 30-60s | Web search only |
| Tech & AI | RSS | Interest | DeepSeek | 10-15s | Always runs |
| ... (8 interest sections) | RSS | Interest | DeepSeek | ~2m total | Always run |
| Legacy queries | Queries file | Fallback | Perplexity | 30-60s | Only if file exists |

---

**End of Architecture Analysis**

Generated: 2025-12-10
Analyzed version: rss_briefing.py (HEAD 25321e0)
