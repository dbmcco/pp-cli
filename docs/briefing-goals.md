# Morning Briefing System - Goals & Requirements

**Date:** 2025-12-10
**Owner:** Braydon

## Primary Goals

1. **Manageable Daily Volume**
   - Brief should be scannable in 10-15 minutes
   - Prioritize quality over quantity
   - Avoid overwhelming amount of content

2. **Day-to-Day Variety**
   - Different content each day of the week
   - Rotating deep dives prevent repetition
   - No identical sections appearing daily

3. **Proper Source Attribution**
   - Every story must include source URL or clear citation
   - Enable follow-up reading on interesting stories
   - Maintain journalistic rigor

4. **Direct Summaries (Not Meta-Summaries)**
   - Summaries should present content directly
   - Avoid phrases like "Based on the provided sources..."
   - No conversational framing or explanations of the summary

5. **Accurate Current Events Context**
   - Reflect current political reality (Trump as president-elect/president in 2025)
   - Timely and contextually accurate references
   - No outdated framings

## Content Preferences

### Daily Core (Every Day)
- **Weather**: Old Lyme, CT
- **Key Headlines**: 3-5 most important global stories (past 48 hours)
- **Connecticut**: State politics + shoreline community news
- **Science Roundup**: Broad coverage across all domains

### Rotating Deep Dives (1-3 per day)
- Schedule varies by day of week
- Academic rigor and evidence-based
- 2-3 paragraphs with depth

### Interest Areas (When Covered)

#### Music (Composer's Perspective)
- Post-minimalism & spectral music
- New compositions, premieres, doctoral programs
- Contemporary trends and techniques
- **NOT**: Standard repertoire, traditional orchestra news

#### AI/Tech (Systems Builder)
- CLI-first tools and frameworks
- AI integration patterns (MCP servers, agent architectures)
- PKM + AI workflow innovations
- Builder/developer-focused content
- **NOT**: Funding rounds, exec moves, generic AI ethics

#### History/Archaeology (Evidence-Based)
- Novel archaeological finds
- Ancient technology breakthroughs
- Climate factors shaping civilizations
- Lost cities and human migration
- **NOT**: Speculative theories, un-scientific claims

#### Design (Systems & Function)
- Product/industrial, architecture, UX/UI
- Information design and data visualization
- Service/system design
- Foundational design principles
- **NOT**: Fashion, interior, pure graphics

#### Science (All Domains)
- Space, medical, climate, physics, neuroscience
- Materials science, energy, biology/genetics
- Evidence-based research, breakthroughs

#### Automotive
- New vehicle releases (cars/motorcycles)
- EV technology, autonomous driving
- Design principles, concept cars
- Manufacturing innovation
- **NOT**: Exotics/supercars, industry business news

#### Cognitive Science
- Academic research on creativity mechanisms
- How intuition functions
- Peer-reviewed sources only

#### Intellectual Trends
- Big ideas, philosophical movements
- Academic discourse
- Cross-disciplinary work

### Always Filter Out
- Celebrity/entertainment (except occasional fun)
- Sports (except Harvard, Colby, Tulane, Charleston)
- True crime
- Lifestyle/wellness trends
- Clickbait and banal reporting

## Technical Requirements

1. **RSS + LLM Hybrid Approach**
   - Use RSS feeds for curated, authoritative sources
   - DeepSeek 3.2 for summarization (cost-effective)
   - Perplexity for deep dives (web search capability)

2. **Directive Prompts**
   - Imperative instructions, not conversational
   - Clear FOCUS/EXCLUDE criteria
   - Specific format requirements

3. **Retry Logic & Resilience**
   - Weather API retries (multiple sources)
   - Graceful degradation when sources unavailable
   - No "I cannot provide..." apologies in output

4. **Output to Obsidian**
   - Append to daily note in `/Users/braydon/Obsidian/Bvault/Daily notes/`
   - Markdown format with proper headings
   - Enable inline feedback mechanism (future)

## Current Problems (As of 2025-12-10)

1. **Volume**: 15-20 sections per day vs target of 4-6
2. **Repetition**: 8 interest sections appearing every single day
3. **Citations**: Missing source URLs in most summaries
4. **Meta-summaries**: DeepSeek producing "Based on..." instead of direct content
5. **Mystery sections**: Extra sections appearing not in config
6. **Variation**: Deep dives getting lost in sea of daily interest sections

## Success Metrics

- Daily brief = 4-6 sections total (not 15-20)
- Each section has clear source citations
- Content varies significantly day-over-day
- Summaries are direct and scannable
- Braydon reads it every morning without feeling overwhelmed
