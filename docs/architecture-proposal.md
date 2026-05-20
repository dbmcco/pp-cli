# Morning Briefing System - Architecture Proposal

**Date:** 2025-12-10
**Author:** Claude (AI Systems Architect)
**Status:** PROPOSAL for Review

---

## Executive Summary

The morning briefing system is producing **15-20 sections daily** instead of the target **4-6 sections**. Root cause is simple: **every interest-based section appears every day, and deep dives are additional**. The fix is architectural, not configurational: shift from "daily + deep dives" to "daily core + rotating interests." DeepSeek's conversational style and missing citations are secondary issues with straightforward solutions.

**Bottom Line:** Move 8 interest sections to a **weekly rotation schedule** alongside existing deep dives. Keep only 3 true daily sections. This delivers 4-7 sections per day with maximum variety.

---

## 1. Gap Analysis: Goals vs Reality

### Volume Gap (CRITICAL)

**Goal:** 4-6 sections per day
**Reality:** 15-20 sections per day
**Variance:** 200-300% over target

**Breakdown of current output:**
- Weather (always) = 1
- Core sections (daily) = 3 (Headlines, Connecticut, Science Roundup)
- **Interest sections (daily)** = **8** (Tech & AI, Hacker News, Classical Music, Automotive, Politics, Archaeological Discoveries, Design Innovations, Cognitive Science)
- Deep dives (rotating) = 1-3
- Legacy query sections = 0-2

**The problem:** 8 interest sections appear **every single day**, then deep dives are **added on top**. This creates 13-16 sections before deep dives even start.

### Variety Gap (MODERATE)

**Goal:** Different content each day of the week
**Reality:** 8 identical sections daily, deep dives provide variety but get lost in volume

**Current pattern:**
```
Monday:    3 core + 8 interests + 3 deep dives = 14 sections
Tuesday:   3 core + 8 interests + 3 deep dives = 14 sections
Wednesday: 3 core + 8 interests + 3 deep dives = 14 sections
```

Day-to-day variety exists only in deep dive topics. The bulk (11 sections) is identical every day.

### Citation Gap (CRITICAL)

**Goal:** Every story includes source URL or clear citation
**Reality:** Citations present in ~40% of stories, often stripped during LLM processing

**Examples from 2025-12-10:**
- ✓ "Australia implements... (Source: The New York Times via Google News)"
- ✗ "MIT researchers propose a method..." (no source)
- ✗ "Solid-state batteries... with automakers like Toyota..." (no source URLs)

**Root causes:**
1. DeepSeek summarization prompt doesn't explicitly require citations
2. Format instructions say "with source attribution" but don't specify URL format
3. Some RSS items lack URLs in the feed itself
4. LLM strips citations during rewriting

### Meta-Summary Gap (MODERATE)

**Goal:** Direct summaries presenting content
**Reality:** ~30% of summaries start with conversational framing

**Examples from output:**
- ✗ "Based on the provided sources from the past 48 hours..."
- ✗ "Based on your criteria to focus on innovative design developments..."
- ✗ "Based on the provided source content and your priorities..."

**Root cause:** DeepSeek's training makes it conversational. Current prompts don't explicitly forbid this pattern.

---

## 2. Root Cause Analysis

### Why Too Much Content?

**Architectural flaw:** The system treats **interests** and **deep dives** as separate, additive categories.

```python
# Current architecture (rss_briefing.py lines 194-236)
core_sections = ["Key Headlines", "Connecticut", "Science Roundup"]  # 3 sections

# Process core sections (daily)
for section_name in core_sections:
    # ...

# Process interest sections (ALSO DAILY - this is the problem!)
interest_sections = [
    "Tech & AI",
    "Hacker News Top Stories",
    "Classical Music",
    "Automotive",
    "Politics",
    "Archaeological Discoveries",
    "Design Innovations",
    "Cognitive Science",
]  # 8 sections every day!

for section_name in interest_sections:
    # ...

# THEN add deep dives on top
deep_dive_topics = DEEP_DIVE_SCHEDULE.get(day_of_week, [])  # +1-3 sections
```

The code literally processes 3 core + 8 interests + 1-3 deep dives = **12-14 sections minimum** before any legacy queries.

**Design intent mismatch:** The original design doc says "Daily Core (Every Day)" vs "Rotating Deep Dives (1-3 per day)" but the implementation makes interests daily AND adds deep dives.

### Why Are Interest Sections Daily?

Looking at `SECTION_FEEDS` (rss_config.py), interest sections have RSS feed configurations with no scheduling logic. The code in `rss_briefing.py` simply iterates through all of them every day.

**There is no rotation mechanism for RSS-based sections.** Only `DEEP_DIVE_SCHEDULE` has day-of-week logic, and those are Perplexity-based.

### Why Do Mystery Sections Appear?

Not actually mystery sections - they're the **8 interest sections** that were supposed to rotate but appear daily instead. Examples:
- "Tech & AI" (should rotate with "AI Workflows & Tools" deep dive)
- "Design Innovations" (duplicates "Design Innovations" deep dive on Monday)
- "Cognitive Science" (same name in RSS interests AND Tuesday deep dives)

There's **naming collision** between RSS sections and deep dive topics.

### Why Are Citations Missing?

**Technical root cause:** RSS feeds provide URLs, but DeepSeek summarization doesn't preserve them.

Flow:
1. `rss_parser.py` extracts items with URLs: `format_items_for_llm()` includes links
2. Content passed to `llm_processor.py`: URLs are in the source text
3. DeepSeek summarization prompt: **doesn't explicitly require URL preservation**
4. DeepSeek output: Rewrites content, drops specific URLs, adds generic attribution

Example from prompt (rss_config.py line 43):
```
Format each as: • **Headline**: Brief summary with source attribution.
```

"Source attribution" is vague - DeepSeek interprets as "(Source: Reuters)" not "(https://reuters.com/article/...)"

**Second issue:** Perplexity deep dives should provide citations automatically, but the code strips them:

```python
# llm_processor.py line 71
if '## Sources' in filtered:
    filtered = filtered.split('## Sources')[0]
```

This **intentionally removes** Perplexity's source URLs.

### Why Is DeepSeek Conversational?

DeepSeek's base model is trained on conversational data. The prompt style enables this:

Current prompt structure (llm_processor.py line 136):
```python
full_prompt = f"""{prompt}

Here is the source content to process:

{content}"""
```

This feels like a conversation: "Here is..." triggers assistant response patterns.

**Prompt engineering fix needed:** Use imperative, directive prompts that position DeepSeek as a content processor, not a conversational assistant.

---

## 3. Architectural Proposal

### Design Principle: Rotating Calendar, Not Additive Layers

**Current (broken):**
```
Every Day = Core + ALL Interests + Deep Dives
Result: 12-14 sections minimum
```

**Proposed:**
```
Every Day = Core + Scheduled Interests + Deep Dives
Result: 4-7 sections total
```

### New Architecture: Unified Rotation Schedule

#### Daily Core (Always Present)
1. **Weather** - Old Lyme, CT
2. **Key Headlines** - 3-5 global stories
3. **Connecticut** - State + shoreline news

**That's it. Only 3 sections every day.**

#### Rotating Content (1-4 per day based on day of week)

**Monday:**
- Contemporary Music Trends (Perplexity deep dive)
- Tech & AI (RSS + DeepSeek)
- Design Innovations (Perplexity deep dive)

**Tuesday:**
- Archaeological Discoveries (RSS + DeepSeek)
- Cognitive Science (RSS + DeepSeek)
- EV & Autonomous Tech (Perplexity deep dive)

**Wednesday:**
- New Music Compositions (Perplexity deep dive)
- AI System Architecture (Perplexity deep dive)
- Intellectual Trends (Perplexity deep dive)

**Thursday:**
- Science Roundup (RSS + DeepSeek) - move from daily to Thursday only
- Automotive (RSS + DeepSeek)
- Design Principles (Perplexity deep dive)

**Friday:**
- Politics (RSS + DeepSeek)
- Hacker News Top Stories (RSS + DeepSeek)
- Week in Review (Perplexity deep dive)

**Weekend:**
- Classical Music (RSS + DeepSeek) - Saturday
- Cultural Events (Perplexity deep dive) - Saturday/Sunday
- Race Calendar (Perplexity deep dive) - when relevant

**Rationale for specific assignments:**

- **Science Roundup moves to Thursday:** Science news accumulates; Thursday gives a week's worth
- **Politics on Friday:** Week's policy developments for weekend reflection
- **Tech & AI on Monday:** Start week with builder-focused content
- **Classical Music weekend:** Aligns with concert schedules
- **Hacker News Friday:** Week's best technical discussions
- **No "Hacker News Top Stories" AND "Tech & AI":** They overlap heavily; alternate instead

**Total per day:**
- Mon-Thu: 3 core + 2-3 rotating = **5-6 sections**
- Friday: 3 core + 3 rotating = **6 sections**
- Weekend: 3 core + 1-2 rotating = **4-5 sections**

**Average: 5.3 sections/day** - right in the target range.

### Architecture Components

#### Component 1: Unified Section Registry

Replace separate `SECTION_FEEDS` and `DEEP_DIVE_SCHEDULE` with single `SECTION_REGISTRY`:

```python
@dataclass
class Section:
    name: str
    type: Literal["rss", "perplexity"]
    schedule: list[str]  # Days of week: ["monday", "wednesday"] or ["daily"]

    # RSS-specific
    feeds: Optional[list[FeedSource]] = None
    summary_prompt: Optional[str] = None

    # Perplexity-specific
    search_prompt: Optional[str] = None

SECTION_REGISTRY: list[Section] = [
    # Core sections
    Section("Weather", type="api", schedule=["daily"]),
    Section("Key Headlines", type="rss", schedule=["daily"], feeds=[...], summary_prompt="..."),
    Section("Connecticut", type="rss", schedule=["daily"], feeds=[...], summary_prompt="..."),

    # Rotating RSS sections
    Section("Tech & AI", type="rss", schedule=["monday"], feeds=[...], summary_prompt="..."),
    Section("Archaeological Discoveries", type="rss", schedule=["tuesday"], feeds=[...], summary_prompt="..."),
    Section("Science Roundup", type="rss", schedule=["thursday"], feeds=[...], summary_prompt="..."),
    Section("Automotive", type="rss", schedule=["thursday"], feeds=[...], summary_prompt="..."),
    Section("Politics", type="rss", schedule=["friday"], feeds=[...], summary_prompt="..."),
    Section("Hacker News Top Stories", type="rss", schedule=["friday"], feeds=[...], summary_prompt="..."),
    Section("Classical Music", type="rss", schedule=["saturday"], feeds=[...], summary_prompt="..."),
    Section("Cognitive Science", type="rss", schedule=["tuesday"], feeds=[...], summary_prompt="..."),

    # Rotating Perplexity sections
    Section("Contemporary Music Trends", type="perplexity", schedule=["monday"], search_prompt="..."),
    Section("AI Workflows & Tools", type="perplexity", schedule=["monday"], search_prompt="..."),
    Section("Design Innovations", type="perplexity", schedule=["monday"], search_prompt="..."),
    Section("EV & Autonomous Tech", type="perplexity", schedule=["tuesday"], search_prompt="..."),
    Section("New Music Compositions", type="perplexity", schedule=["wednesday"], search_prompt="..."),
    Section("AI System Architecture", type="perplexity", schedule=["wednesday"], search_prompt="..."),
    Section("Intellectual Trends", type="perplexity", schedule=["wednesday"], search_prompt="..."),
    Section("Design Principles", type="perplexity", schedule=["thursday"], search_prompt="..."),
    Section("Week in Review", type="perplexity", schedule=["friday"], search_prompt="..."),
    Section("Cultural Events", type="perplexity", schedule=["saturday", "sunday"], search_prompt="..."),
]
```

#### Component 2: Day-of-Week Scheduler

```python
def get_sections_for_day(day_of_week: str) -> list[Section]:
    """Get all sections scheduled for a specific day"""
    return [
        section for section in SECTION_REGISTRY
        if "daily" in section.schedule or day_of_week in section.schedule
    ]
```

#### Component 3: Enhanced DeepSeek Prompts

**Directive, imperative style with explicit citation requirements:**

```python
summary_prompt = """Extract the 3-5 most important stories. Output ONLY the formatted list.

REQUIRED FORMAT:
• **Headline**: Summary with specific impact. (Source: Publication Name, URL)

CRITICAL: Include the full source URL from the provided content in parentheses.

FOCUS: [domain-specific criteria]
EXCLUDE: [domain-specific exclusions]

DO NOT include conversational framing like "Based on the provided sources" or "Here are the stories". Output the bullet list directly."""
```

**Example for Key Headlines:**

```python
summary_prompt = """Extract the 3-5 most important global news stories. Output ONLY the formatted list.

REQUIRED FORMAT:
• **Headline**: Brief summary. (https://source-url.com/article)

CRITICAL: Every item MUST include the full URL from the source content.

PRIORITIZE: Breaking news, major policy, significant global events.
EXCLUDE: Celebrity, entertainment, sports, true crime, lifestyle.

Output the bullet list directly without conversational framing."""
```

#### Component 4: Citation Preservation Pipeline

**Change 1:** Don't strip Perplexity sources

```python
# llm_processor.py - REMOVE this block:
if '## Sources' in filtered:
    filtered = filtered.split('## Sources')[0]

# REPLACE with:
# Keep sources section - it's valuable!
```

**Change 2:** Enforce URL format in RSS prompts

Update all `summary_prompt` in `SECTION_REGISTRY` to require:
```
(Source Name, https://full-url.com)
```

**Change 3:** RSS parser provides URLs more clearly

In `format_items_for_llm()`, make URLs more prominent:

```python
def format_items_for_llm(items: list[FeedItem]) -> str:
    formatted = []
    for i, item in enumerate(items, 1):
        formatted.append(f"{i}. [{item.source}] {item.title}")
        formatted.append(f"   Summary: {item.summary}")
        formatted.append(f"   URL: {item.link}")  # Make URL explicit
        formatted.append(f"   Date: {item.date}")
        formatted.append("")
    return '\n'.join(formatted)
```

#### Component 5: Simplified Main Loop

```python
def main():
    today = datetime.now().strftime('%Y-%m-%d')
    day_of_week = datetime.now().strftime('%A').lower()

    # Get weather
    weather = get_weather()

    # Get scheduled sections for today
    sections = get_sections_for_day(day_of_week)

    results = []

    # Process each section
    for section in sections:
        if section.type == "rss":
            content = process_section_with_rss(section)
        elif section.type == "perplexity":
            content = run_perplexity_query(section.search_prompt)

        if content:
            results.append((section.name, content))

    # Build and write briefing
    write_briefing(results, weather, today)
```

**No more separate loops for core/interest/deep_dive.** Single unified loop.

---

## 4. Implementation Plan

### Phase 1: Fix Volume (IMMEDIATE - Day 1)

**Goal:** Get to 4-7 sections per day

**Tasks:**
1. Create `SECTION_REGISTRY` with unified schedule
2. Move 8 interest sections to day-specific schedules:
   - Tech & AI → Monday
   - Archaeological Discoveries → Tuesday
   - Cognitive Science → Tuesday
   - Science Roundup → Thursday (move from daily)
   - Automotive → Thursday
   - Politics → Friday
   - Hacker News → Friday
   - Classical Music → Saturday
   - Design Innovations → Remove (covered by Perplexity deep dive)
3. Update `rss_briefing.py` main loop to use `get_sections_for_day()`
4. Remove separate `interest_sections` loop
5. **Test with dry-run for each day of week**

**Validation:**
```bash
# Test each day
for day in monday tuesday wednesday thursday friday saturday sunday; do
    # Modify script to accept day override
    ./rss_briefing.py --day $day --dry-run | grep "^###" | wc -l
    # Should output 4-7 for each day
done
```

**Time estimate:** 2-3 hours (includes testing)

### Phase 2: Fix Citations (Day 2)

**Goal:** Every story includes source URL

**Tasks:**
1. Update all `summary_prompt` strings in `SECTION_REGISTRY` to require URL format:
   ```
   • **Headline**: Summary. (https://source-url.com)
   ```
2. Modify `format_items_for_llm()` to make URLs more explicit
3. **Remove** the source-stripping code from `llm_processor.py` (lines 71-72, 108-109, 184-185)
4. Add post-processing validator:
   ```python
   def validate_citations(content: str, section_name: str) -> bool:
       """Warn if content lacks URLs"""
       has_urls = bool(re.search(r'https?://', content))
       if not has_urls:
           print(f"Warning: {section_name} has no citation URLs", file=sys.stderr)
       return has_urls
   ```
5. **Test with sample runs, manually inspect citations**

**Time estimate:** 2 hours

### Phase 3: Fix Meta-Summaries (Day 2)

**Goal:** Direct summaries without conversational framing

**Tasks:**
1. Update all prompts to include:
   ```
   DO NOT include conversational framing like "Based on the provided sources" or
   "Here are the stories". Output the bullet list directly.
   ```
2. Add explicit instruction at top of prompt:
   ```
   Extract [N] items. Output ONLY the formatted list.
   ```
3. Add post-processing filter:
   ```python
   def strip_meta_framing(content: str) -> str:
       """Remove conversational wrapper if present"""
       lines = content.split('\n')
       # Skip lines that are meta-commentary
       filtered = []
       for line in lines:
           if line.strip().startswith(('Based on', 'Here are', 'Here is',
                                        'The following', 'I have selected')):
               continue
           filtered.append(line)
       return '\n'.join(filtered)
   ```
4. **Test with multiple DeepSeek runs**

**Time estimate:** 1 hour

### Phase 4: Testing & Validation (Day 3)

**Goal:** Verify fixes work across entire week

**Tasks:**
1. Generate dry-run briefings for entire week
2. Validate section counts:
   ```bash
   for day in monday tuesday wednesday thursday friday saturday sunday; do
       count=$(./rss_briefing.py --day $day --dry-run | grep "^###" | wc -l)
       echo "$day: $count sections"
       [[ $count -ge 4 && $count -le 7 ]] || echo "  ❌ OUT OF RANGE"
   done
   ```
3. Manually review citation presence in each section
4. Manually review for meta-commentary in DeepSeek outputs
5. Check day-to-day variety (no section appears all 7 days except core 3)
6. **Generate feedback checklist for Braydon**

**Time estimate:** 2 hours

### Phase 5: Migration (Day 3)

**Goal:** Deploy to production

**Tasks:**
1. Backup current `rss_config.py` and `rss_briefing.py`
2. Deploy new code
3. Run first production briefing next morning
4. Monitor for 1 week
5. Collect feedback from Braydon via Obsidian inline comments
6. Iterate on prompt refinements as needed

**Time estimate:** 1 hour deploy + 1 week monitoring

---

## 5. Specific Code Changes

### Change 1: rss_config.py

**Remove:**
- `SECTION_FEEDS` dict (lines 29-245)
- `DEEP_DIVE_SCHEDULE` dict (lines 249-257)
- `DEEP_DIVE_PROMPTS` dict (lines 260-414)

**Replace with:**
- `SECTION_REGISTRY` list of `Section` objects
- Single source of truth for all sections
- Each section has schedule field: `["daily"]` or `["monday", "wednesday"]`

### Change 2: rss_briefing.py

**Remove:**
- `core_sections` list (line 194)
- `interest_sections` list (line 220)
- Three separate processing loops (lines 200-252)

**Replace with:**
- `sections = get_sections_for_day(day_of_week)` (single call)
- Single processing loop iterating `sections`
- Type dispatch: `if section.type == "rss"` vs `"perplexity"`

### Change 3: llm_processor.py

**Remove:**
- Lines 71-72: Source stripping for Perplexity
- Lines 108-109: Source stripping (duplicate)
- Lines 184-185: Source stripping (duplicate)

**Add:**
- `strip_meta_framing()` function
- `validate_citations()` function
- Apply both in `process_rss_content()` before return

### Change 4: All prompt strings

**Add to every prompt:**
```
REQUIRED FORMAT:
• **Headline**: Summary. (https://source-url.com)

CRITICAL: Include the full source URL.

DO NOT include conversational framing. Output the bullet list directly.
```

---

## 6. Why This Works

### Solves Volume Problem

**Math:**
- Core: 3 sections (daily)
- Rotating: 1-4 sections (varies by day)
- Total: 4-7 sections ✓

**Mechanism:** No section appears daily unless explicitly in core. Interest topics rotate through the week.

### Solves Variety Problem

**Day-to-day comparison:**

Before:
```
Monday:    Headlines, CT, Science, Tech, HN, Music, Auto, Politics, Arch, Design, CogSci = 11 same
Tuesday:   Headlines, CT, Science, Tech, HN, Music, Auto, Politics, Arch, Design, CogSci = 11 same
Wednesday: Headlines, CT, Science, Tech, HN, Music, Auto, Politics, Arch, Design, CogSci = 11 same
```

After:
```
Monday:    Headlines, CT, Music Trends, Tech, Design
Tuesday:   Headlines, CT, Archaeology, CogSci, EV Tech
Wednesday: Headlines, CT, New Compositions, AI Architecture, Intellectual
Thursday:  Headlines, CT, Science Roundup, Automotive, Design Principles
Friday:    Headlines, CT, Politics, HN Stories, Week Review
```

**Only 3 sections repeat across all days.** The other 2-4 are unique per day.

### Solves Citation Problem

**Multiple reinforcements:**
1. Prompt explicitly requires URL in format string
2. RSS parser highlights URL on separate line
3. Perplexity sources no longer stripped
4. Validator warns if URLs missing

**Failure modes reduced:** Even if DeepSeek drops URLs, validator catches it.

### Solves Meta-Summary Problem

**Two-layer defense:**
1. Prompt explicitly forbids framing with examples
2. Post-processor strips it if it appears anyway

**DeepSeek learns from examples:** Showing bad patterns to avoid works better than just saying "be direct."

---

## 7. Risks & Mitigations

### Risk 1: Some days feel "light"

**Example:** Wednesday has 3 Perplexity deep dives, no RSS sections beyond core.

**Mitigation:** Perplexity deep dives are meatier (2-3 paragraphs). Three deep dives = substantial content. If needed, add one RSS section to Wednesday (e.g., "Design Innovations" RSS).

**Monitoring:** Track Braydon feedback for 2 weeks. If Wednesday consistently feels thin, add 1 RSS section.

### Risk 2: Missing a topic on its off-days

**Example:** Want automotive news on Monday, but it's scheduled for Thursday.

**Mitigation:**
1. Core sections (Headlines) may cover major automotive news
2. Week in Review (Friday) recaps big stories from Mon-Thu
3. Can always add override via legacy query files for special cases

**Long-term:** Build "topic override" mechanism where Braydon can say "@briefing add Automotive to tomorrow" via Obsidian.

### Risk 3: RSS feed quality varies

**Example:** Thursday has Science Roundup + Automotive, but both feeds have no interesting items.

**Mitigation:**
1. Existing behavior: Empty sections are skipped
2. Fallback: If <3 sections generated, pull from next day's schedule as bonus
3. Quality thresholds: LLM can return empty string if nothing meets criteria

**This risk exists in current system too.** Not introducing new fragility.

### Risk 4: DeepSeek ignores citation instructions

**Example:** Prompt says "include URL" but DeepSeek still drops them.

**Mitigation:**
1. Validator flags the issue in console
2. Post-processor can attempt to reattach URLs from source data
3. Ultimate fallback: Switch to Claude API for summarization (slower, more expensive, but more reliable)
4. Hybrid approach: Use DeepSeek, but if validator fails >2 times for a section, flag for manual review

**Test this extensively in Phase 2.** If DeepSeek compliance is <80%, recommend Claude.

---

## 8. Success Metrics

### Week 1 Targets

- [ ] Daily section count: 4-7 (measured each day)
- [ ] Citation presence: >80% of stories have source URLs
- [ ] Meta-summary frequency: <10% of sections start with conversational framing
- [ ] Variety score: No section appears >3 days/week (except core 3)

### Week 2 Targets

- [ ] Daily section count: 4-6 (tighter range)
- [ ] Citation presence: >90%
- [ ] Meta-summary frequency: <5%
- [ ] Braydon feedback: Qualitative assessment of "scannable in 10-15 minutes"

### Month 1 Targets

- [ ] Stable 4-6 sections per day
- [ ] Citation presence: >95%
- [ ] No meta-summaries
- [ ] Braydon reads briefing every morning without feeling overwhelmed
- [ ] Day-to-day content feels distinct and varied

---

## 9. Alternatives Considered

### Alternative 1: Keep all sections, use LLM to pick top 5

**Approach:** Generate all sections, then use Claude to select "most interesting 5" based on criteria.

**Rejected because:**
- Expensive: Would hit RSS feeds + DeepSeek + Claude every day
- Opaque: Braydon wouldn't know what got cut
- Inconsistent: LLM picks vary, topics might never appear
- Defeats purpose: Point is to rotate interests, not randomly sample

### Alternative 2: User configuration file

**Approach:** Braydon edits YAML file each Sunday specifying week's interests.

**Rejected because:**
- Maintenance burden: Requires weekly manual configuration
- Decision fatigue: Forces Braydon to plan week ahead
- Defeats automation: System should be intelligent default, not requiring oversight

**Might revisit** as optional override mechanism later.

### Alternative 3: Keep daily interests, make them shorter

**Approach:** Keep 8 interest sections daily but limit to 1-2 items each.

**Rejected because:**
- Still ~11 sections with 2 items each = lots of context switching
- Loses depth: 1-2 items isn't enough to get value from a section
- Doesn't solve variety: Same 8 topics every day still feels repetitive

### Alternative 4: Move everything to Perplexity deep dives

**Approach:** Drop RSS feeds entirely, use Perplexity web search for all sections.

**Rejected because:**
- Cost: Perplexity API is more expensive than RSS + DeepSeek
- Timeliness: Perplexity web search may miss very recent RSS items
- Quality: Curated RSS feeds (Nature, NPR, etc.) are higher quality than web scraping
- Reliability: RSS feeds are more stable than web search APIs

**Current hybrid is optimal:** RSS for volume/cost, Perplexity for depth/augmentation.

---

## 10. Recommendation

**Implement the proposed architecture in 3-day sprint:**

- **Day 1:** Phase 1 (fix volume) - 3 hours
- **Day 2:** Phase 2 (citations) + Phase 3 (meta-summaries) - 3 hours
- **Day 3:** Phase 4 (testing) + Phase 5 (deploy) - 3 hours

**Total effort:** ~9 hours of focused development + 1 week of monitoring.

**Expected outcome:**
- Briefing drops from 15-20 sections to 4-7 sections (70% reduction)
- Day-to-day variety increases dramatically (only 3/7 sections repeat)
- Citations present in >90% of stories
- Direct summaries without meta-commentary

**Confidence level:** High. The root cause is clear (architectural, not configurational), the fix is straightforward (unified scheduling), and the implementation is low-risk (no changes to RSS parsing, LLM APIs, or data flow—just scheduling logic and prompt refinement).

**Priority:** IMMEDIATE. Current system is 3x over target volume. Braydon is likely skimming or skipping sections, defeating the purpose of personalization.

---

## Appendix A: Weekly Schedule Visual

```
           Mon    Tue    Wed    Thu    Fri    Sat    Sun
CORE
Headlines    ✓      ✓      ✓      ✓      ✓      ✓      ✓
Connecticut  ✓      ✓      ✓      ✓      ✓      ✓      ✓

ROTATING
Music Trends ✓      -      -      -      -      -      -
Tech & AI    ✓      -      -      -      -      -      -
Design Innov ✓      -      -      -      -      -      -

Archaeology  -      ✓      -      -      -      -      -
CogSci       -      ✓      -      -      -      -      -
EV Tech      -      ✓      -      -      -      -      -

New Music    -      -      ✓      -      -      -      -
AI Systems   -      -      ✓      -      -      -      -
Intellectual -      -      ✓      -      -      -      -

Science      -      -      -      ✓      -      -      -
Automotive   -      -      -      ✓      -      -      -
Design Princ -      -      -      ✓      -      -      -

Politics     -      -      -      -      ✓      -      -
HN Stories   -      -      -      -      ✓      -      -
Week Review  -      -      -      -      ✓      -      -

Classical    -      -      -      -      -      ✓      -
Cultural     -      -      -      -      -      ✓      ✓

TOTAL        5      5      5      5      6      4      3
```

**Note:** Science Roundup moved from "daily" to Thursday only. Provides full week of discoveries.

---

## Appendix B: Example Revised Prompt (Key Headlines)

**Current (broken):**
```
Select the 3-5 most important global news stories from the past 48 hours only.

EXCLUDE: Celebrity/entertainment, sports, true crime, lifestyle trends.
PRIORITIZE: Breaking news, major policy developments, significant global events.

Format each as: • **Headline**: Brief summary with source attribution.
```

**Proposed (fixed):**
```
Extract the 3-5 most important global news stories. Output ONLY the formatted list.

REQUIRED FORMAT:
• **Headline**: Brief summary. (https://source-url.com)

CRITICAL: Every item MUST include the full URL from the source content.

PRIORITIZE: Breaking news, major policy, significant global events from past 48 hours.
EXCLUDE: Celebrity, entertainment, sports, true crime, lifestyle trends.

DO NOT include conversational framing like "Based on the provided sources" or "Here are the stories".
Output the bullet list directly.
```

**Changes:**
1. First line sets expectation: "Output ONLY the formatted list"
2. FORMAT section shows exact pattern including URL
3. CRITICAL emphasizes URL requirement
4. DO NOT explicitly forbids meta-commentary with examples
5. More directive tone throughout ("Extract", "Output", "MUST")

---

## Appendix C: Implementation Checklist

**Phase 1: Fix Volume**
- [ ] Create `Section` dataclass in rss_config.py
- [ ] Create `SECTION_REGISTRY` with all sections and schedules
- [ ] Implement `get_sections_for_day(day: str) -> list[Section]`
- [ ] Modify rss_briefing.py main() to use unified loop
- [ ] Remove separate core/interest/deep_dive lists
- [ ] Add `--day` flag for testing
- [ ] Test all 7 days, verify 4-7 sections each
- [ ] Verify Science Roundup only appears Thursday

**Phase 2: Fix Citations**
- [ ] Update all summary_prompt strings to require URL format
- [ ] Modify format_items_for_llm() to highlight URLs
- [ ] Remove source-stripping code (3 locations in llm_processor.py)
- [ ] Implement validate_citations() function
- [ ] Add citation validator to main processing loop
- [ ] Test sample runs, inspect output manually
- [ ] Verify >80% of stories have URLs

**Phase 3: Fix Meta-Summaries**
- [ ] Add anti-framing instructions to all prompts
- [ ] Implement strip_meta_framing() function
- [ ] Apply strip_meta_framing() to all DeepSeek outputs
- [ ] Test multiple runs with DeepSeek
- [ ] Verify <10% have conversational framing

**Phase 4: Testing**
- [ ] Generate dry-run for all 7 days
- [ ] Count sections per day (all 4-7)
- [ ] Check citation presence (>80%)
- [ ] Check meta-summary frequency (<10%)
- [ ] Verify day-to-day variety
- [ ] Create feedback form for Braydon

**Phase 5: Deploy**
- [ ] Backup current code
- [ ] Deploy new code
- [ ] Run first production briefing
- [ ] Monitor for 1 week
- [ ] Collect Braydon feedback
- [ ] Iterate on prompts as needed

---

**END OF PROPOSAL**

This architecture will deliver on all stated goals: 4-6 scannable sections, day-to-day variety, proper citations, and direct summaries. The fix is surgical—unified scheduling plus prompt refinement—not a full rewrite. Ready to implement immediately.
