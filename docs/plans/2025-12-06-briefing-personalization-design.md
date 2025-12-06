# Briefing Personalization Design
**Date:** 2025-12-06
**Status:** Approved

## Overview
Redesign daily briefing to provide personalized, varied content based on Braydon's specific interests with rotating deep dives instead of repetitive daily sections.

## Core Principles
1. **Academic rigor over clickbait** - Well-researched, evidence-based content
2. **Variety over repetition** - Rotate deep dive topics daily
3. **Builder-focused tech** - Tools and techniques, not industry drama
4. **Composer's perspective on music** - New works and trends, not standard repertoire
5. **Flexible depth** - 1-3 deep dives per day based on what's interesting

## Interest Map

### Daily/Regular Coverage

#### Music (Composer's Perspective)
- Post-minimalism & spectral music (primary)
- New compositions including doctoral programs
- Contemporary music trends & compositional techniques
- Organizations premiering new works
- **NOT**: Standard repertoire, traditional orchestra news

#### AI/Tech (Systems Builder)
- CLI-first tools and frameworks
- AI integration architectures (MCP servers, agent frameworks)
- PKM + AI workflow innovations
- Audio → structured data pipelines
- Builder/developer-focused technical content
- **NOT**: Funding rounds, exec moves, generic AI ethics

#### History (Evidence-Based Discovery)
- Novel early archaeological finds
- Ancient technology breakthroughs
- Climate/environmental factors shaping civilizations
- Lost cities and cultures
- Human migration and origins
- Macro historical trends that defined eras
- **NOT**: Speculative timeline rewrites, un-scientific theories

#### Design (Systems & Function)
- Product/industrial design
- Architecture
- UI/UX design
- Information design (data visualization, knowledge representation)
- Service/system design
- Foundational design principles
- **NOT**: Fashion, interior design, pure graphics

#### Science (Broad Interest)
- Space exploration (missions, discoveries, technology)
- Medical/health research (breakthroughs, longevity)
- Climate science (research, impacts, solutions)
- Physics/astronomy (fundamental discoveries)
- Neuroscience/psychology
- Materials science
- Energy innovations (fusion, renewables, grid)
- Biology/genetics (CRISPR, evolution, ecosystems)

#### Automotive
- New vehicle releases (cars and motorcycles)
- EV technology advances
- Autonomous driving progress
- Design principles & concept cars
- Manufacturing innovation
- International automotive trends
- **NOT**: Exotic/supercars, industry business news

#### Cognitive Science
- Academic research on creativity mechanisms
- How intuition functions
- Creative thought processes

#### Intellectual Trends
- Big ideas and philosophical movements
- Academic discourse and emerging thought

#### Science Fiction
- New releases (books, notable adaptations)
- Literary trends and movements
- **NOTE**: For enjoyment, not academic analysis

#### Connecticut
- State politics
- Shoreline community news (Old Lyme, Old Saybrook, Essex, Lyme, etc.)
- Topics: local government, education, environmental/coastal, cultural events, state budget/taxes, transportation/infrastructure
- **Scope**: Current balance of state + shoreline is good

#### Athletics
- Half marathons & triathlons near Old Lyme, CT
- Upcoming race calendars

### Periodic Topics (Only When Significant)
- **Haiti**: Recent news and history
- **Russian culture**: Literature, cultural trends (not heavy news)
- **Parental alienation**: Research and legal developments
- **Men's style**: Guidance for 54yo professional evolving beyond preppy/conservative

### Sports Exceptions (Otherwise Filter Out)
- Harvard Football
- Colby College
- Tulane University
- College of Charleston

### Filter Out Completely
- Celebrity/entertainment (except occasional fun)
- Sports (except the 4 colleges above)
- True crime
- Lifestyle/wellness trends (mostly)
- Clickbait, AI-generated headlines, banal reporting

## New Briefing Structure

### Daily Core Sections (Every Day)
1. **Weather** - Old Lyme, CT
2. **Key Headlines** - 3-5 most important global stories (past 48 hours)
3. **Connecticut** - State politics + shoreline community
4. **Science Roundup** - Rotating coverage across all science domains

### Rotating Deep Dives (1-3 per day)

**Monday**
- Contemporary Music Trends
- AI Workflows & Tools
- Design Innovations

**Tuesday**
- Archaeological Discoveries
- Cognitive Science Research
- EV & Autonomous Tech

**Wednesday**
- New Music Compositions & Premieres
- AI System Architecture
- Intellectual Trends

**Thursday**
- Materials Science & Manufacturing
- Design Principles
- Automotive Releases & Concepts

**Friday**
- Week in Review (comprehensive)
- New Sci-Fi Releases (monthly rotation)
- Weekend Event Preview

**Weekend**
- Cultural Events (concerts, races, local happenings)
- Occasional Topics (if significant developments)
- Race Calendar (upcoming half marathons/triathlons)

### Deep Dive Specifications
- **Length**: 2-3 paragraphs (300-500 words)
- **Rigor**: Academic sources when applicable
- **Flexibility**: 1-3 deep dives per day based on available content quality
- **Selection**: Choose topics with substantial new developments

## Feedback System Integration

### Inline Feedback Format
```markdown
### Section Name
%% feedback q:4 r:5 i:more %%

Content...

• **Story headline**
%% feedback q:3 r:4 i:same notes:"Too technical" %%
```

### Feedback Dimensions
- `q:1-5` = Quality rating
- `r:1-5` = Relevance rating
- `i:more|same|less` = Interest level
- `notes:"text"` = Optional notes
- `context:tag` = Optional context tags

### Feedback Storage
- **File**: `feedback-db.json`
- **Structure**: Raw ratings + aggregated stats + day-of-week breakdowns
- **Usage**: Future Claude sessions read JSON and adjust config based on patterns

### Guidance for Future Claude
Document: `docs/feedback-interpretation-guide.md`

**Key principles:**
- Relevance < 3.0 → Reduce coverage or make day-specific
- Relevance > 4.5 → Increase coverage
- Interest "less" > 60% → Consider removing or reducing
- Interest "more" > 60% → Expand coverage, add deep dives
- Day-of-week variance > 1.5 points → Create day-specific configs
- Quality issues in notes → Tune LLM prompts

## Implementation Priorities

### Phase 1: Fix Current Issues (Immediate)
1. **Improve DeepSeek prompts** - Remove conversational tone, make directive
2. **Add weather retry logic** - Already implemented
3. **Remove failed sections** - Don't show "I cannot provide..." apologies

### Phase 2: Implement Interest Map (Next)
1. **Update RSS sources** - Add sources for new interest areas
2. **Create day-specific configs** - Rotate deep dive topics
3. **Rewrite prompts** - Match specific interests and academic rigor requirements
4. **Add new sections** - Science Roundup, Cognitive Science, etc.

### Phase 3: Feedback System (After Testing)
1. **Create feedback parser** - Extract `%% feedback %%` comments from daily notes
2. **Build feedback-db.json** - Store and aggregate ratings
3. **Write interpretation guide** - Help future Claude use feedback
4. **Add feedback templates** - Make it easy to add ratings

### Phase 4: Continuous Improvement (Ongoing)
1. **Monitor feedback** - Review aggregated stats monthly
2. **Tune prompts** - Based on quality and relevance ratings
3. **Adjust sources** - Based on story-level ratings
4. **Refine scheduling** - Based on day-of-week patterns

## Success Criteria
- No more repetitive deep dives on same topics daily
- Content matches specific interests (composer, systems builder, evidence-based)
- Academic rigor maintained across all content
- 1-3 varied deep dives per day
- Feedback system enables continuous improvement
- Higher engagement with briefing content
