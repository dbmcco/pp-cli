#!/Users/braydon/projects/experiments/pp/scripts/venv/bin/python3

# ABOUTME: Unified RSS and Perplexity configuration for morning briefing
# ABOUTME: Single registry with day-of-week scheduling for all sections

from dataclasses import dataclass
from typing import Optional, Literal


@dataclass
class FeedSource:
    """Single RSS feed source with metadata"""
    name: str
    url: str
    priority: int = 1  # Lower = higher priority for deduplication
    max_items: int = 10


@dataclass
class Section:
    """Unified section configuration for RSS or Perplexity content"""
    name: str
    type: Literal["rss", "perplexity"]
    schedule: list[str]  # Days of week: ["monday", "wednesday"] or ["daily"]

    # RSS-specific fields
    feeds: Optional[list[FeedSource]] = None
    summary_prompt: Optional[str] = None
    max_items: int = 5

    # Perplexity-specific fields
    search_prompt: Optional[str] = None


# Unified section registry with scheduling
SECTION_REGISTRY: list[Section] = [

    # ========== DAILY CORE SECTIONS (Weather handled separately) ==========

    Section(
        name="Key Headlines",
        type="rss",
        schedule=["daily"],
        feeds=[
            FeedSource("Google News", "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en", priority=1),
            FeedSource("NPR Top Stories", "https://feeds.npr.org/1001/rss.xml", priority=2),
            FeedSource("BBC News", "http://feeds.bbci.co.uk/news/rss.xml", priority=3),
        ],
        summary_prompt="""Extract the 3-5 most important global news stories from the past 48 hours. Output ONLY the formatted list.

REQUIRED FORMAT:
• **Headline**: Brief summary with specific impact. (Source: Publication, https://full-url.com)

CRITICAL: Include the full source URL from the provided content.

PRIORITIZE: Breaking news, major policy developments, significant global events.
EXCLUDE: Celebrity/entertainment, sports, true crime, lifestyle trends.
CONTEXT: As of December 2025, Donald Trump is president-elect/incoming president, not "former president".

DO NOT include conversational framing like "Based on the provided sources". Output the bullet list directly.""",
        max_items=5,
    ),

    Section(
        name="Connecticut",
        type="rss",
        schedule=["daily"],
        feeds=[
            FeedSource("CT Mirror", "https://ctmirror.org/feed", priority=1),
            FeedSource("Hartford Courant", "https://courant.com/feed", priority=2),
            FeedSource("CT News Junkie", "https://ctnewsjunkie.com/feed/", priority=3),
        ],
        summary_prompt="""Extract 2-3 most relevant Connecticut stories. Output ONLY the formatted list.

REQUIRED FORMAT:
• **Headline**: Brief summary with location context. (https://source-url.com)

CRITICAL: Include full URL from source content.

PRIORITIZE: State politics, shoreline community news (Old Lyme, Old Saybrook, Essex, Lyme).
FOCUS: Local government, education, environmental/coastal, cultural events, state budget/taxes, transportation.

DO NOT include conversational framing. Output bullet list directly.""",
        max_items=3,
    ),

    # ========== MONDAY SECTIONS ==========

    Section(
        name="Tech & AI",
        type="rss",
        schedule=["monday"],
        feeds=[
            FeedSource("Hacker News", "https://news.ycombinator.com/rss", priority=1, max_items=15),
            FeedSource("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index", priority=2),
            FeedSource("The Verge", "https://theverge.com/rss/index.xml", priority=3),
            FeedSource("TechCrunch", "https://techcrunch.com/feed", priority=4),
        ],
        summary_prompt="""Extract 3-5 most significant stories for systems builders and AI integrators. Output ONLY the formatted list.

REQUIRED FORMAT:
• **Tool/Project Name**: What it does and why it matters technically. (https://source-url.com)

CRITICAL: Include full URL.

FOCUS ON:
- CLI tools and frameworks
- AI integration patterns (MCP servers, agent architectures)
- Developer tools and workflows
- Technical implementations (not announcements)
- Open source projects with substance

EXCLUDE: Funding rounds, executive moves, generic AI ethics, industry drama.

DO NOT include conversational framing. Output bullet list directly.""",
        max_items=5,
    ),

    Section(
        name="Contemporary Music Trends",
        type="perplexity",
        schedule=["monday"],
        search_prompt="""Search for current trends in contemporary classical music composition.

FOCUS ON:
- Post-minimalism and spectral music developments
- New compositional techniques and approaches
- Emerging composers and doctoral programs
- Contemporary music festivals and commissions
- Cross-pollination with technology (AI composition, new notation)

Provide 2-3 paragraphs with academic rigor.""",
    ),

    Section(
        name="Design Innovations",
        type="perplexity",
        schedule=["monday"],
        search_prompt="""Search for recent innovative design projects and developments.

FOCUS ON:
- Product/industrial design breakthroughs
- Architectural innovations
- UX/interface design patterns
- Information design and data visualization
- Service/system design methodologies

EXCLUDE: Fashion, interior decoration, pure graphic design.

Provide 2-3 paragraphs on most significant projects.""",
    ),

    # ========== TUESDAY SECTIONS ==========

    Section(
        name="Archaeological Discoveries",
        type="rss",
        schedule=["tuesday"],
        feeds=[
            FeedSource("Archaeology News", "https://www.archaeology.org/feed", priority=1),
            FeedSource("Heritage Daily", "https://www.heritagedaily.com/feed", priority=2),
        ],
        summary_prompt="""Extract notable archaeological findings with academic rigor. Output ONLY the formatted list.

REQUIRED FORMAT:
• **Discovery**: What was found, where, and what it reveals. (https://source-url.com)

CRITICAL: Include full URL.

PRIORITIZE:
- Novel early history discoveries
- Ancient technology breakthroughs
- Climate/environmental impacts on civilizations
- Lost cities and cultures
- Human migration and origins evidence

EXCLUDE: Speculative timeline rewrites, sensationalist claims.

DO NOT include conversational framing. Output bullet list directly.""",
        max_items=2,
    ),

    Section(
        name="Cognitive Science",
        type="rss",
        schedule=["tuesday"],
        feeds=[
            FeedSource("Psychology Today", "https://www.psychologytoday.com/us/front/feed", priority=1),
            FeedSource("ScienceDaily Neuroscience", "https://www.sciencedaily.com/rss/mind_brain.xml", priority=2),
        ],
        summary_prompt="""Extract academic research on creativity and intuition mechanisms. Output ONLY the formatted list.

REQUIRED FORMAT:
• **Research Finding**: What the study reveals about creative/intuitive processes. (https://source-url.com)

CRITICAL: Include full URL.

FOCUS ON:
- How creativity functions neurologically
- Mechanisms of intuitive thought
- Cognitive processes in creative work
- Academic studies with rigor

EXCLUDE: Pop psychology, self-help, speculative theories.

DO NOT include conversational framing. Output bullet list directly.""",
        max_items=2,
    ),

    Section(
        name="EV & Autonomous Tech",
        type="perplexity",
        schedule=["tuesday"],
        search_prompt="""Search for recent developments in electric vehicles and autonomous driving.

FOCUS ON:
- Battery technology advances
- Charging infrastructure innovations
- Autonomous driving technical progress
- Real-world testing and deployment

Provide 2-3 paragraphs with technical depth.""",
    ),

    # ========== WEDNESDAY SECTIONS ==========

    Section(
        name="New Music Compositions",
        type="perplexity",
        schedule=["wednesday"],
        search_prompt="""Search for recent world premieres, commissions, and new works by living composers.

FOCUS ON:
- Contemporary classical premieres in past month
- Organizations commissioning/performing new works
- Living composers releasing major works
- Doctoral composition programs and graduate work
- Post-minimal and spectral music specifically

Provide 2-3 paragraphs with specific works and composers.""",
    ),

    Section(
        name="AI System Architecture",
        type="perplexity",
        schedule=["wednesday"],
        search_prompt="""Search for technical articles on AI integration architectures and patterns.

FOCUS ON:
- MCP (Model Context Protocol) implementations
- Agent coordination frameworks
- Context management and memory systems
- Tool-calling architectures
- Production AI system design patterns

Provide 2-3 paragraphs with technical depth.""",
    ),

    Section(
        name="Intellectual Trends",
        type="perplexity",
        schedule=["wednesday"],
        search_prompt="""Search for emerging ideas and philosophical movements.

FOCUS ON:
- Big ideas in philosophy and social thought
- Academic discourse and new frameworks
- Intellectual movements gaining traction
- Cross-disciplinary intellectual work

Provide 2-3 paragraphs from academic sources.""",
    ),

    # ========== THURSDAY SECTIONS ==========

    Section(
        name="Science Roundup",
        type="rss",
        schedule=["thursday"],
        feeds=[
            FeedSource("Nature News", "https://www.nature.com/nature.rss", priority=1),
            FeedSource("Science News", "https://www.sciencenews.org/feed", priority=2),
            FeedSource("Phys.org", "https://phys.org/rss-feed/", priority=3),
        ],
        summary_prompt="""Extract 3-4 most significant scientific discoveries or developments. Output ONLY the formatted list.

REQUIRED FORMAT:
• **Discovery/Development**: What was found and why it matters. (https://source-url.com)

CRITICAL: Include full URL.

COVERAGE: Space, medical, climate, physics, neuroscience, materials, energy, biology.
FOCUS ON: Evidence-based research, academic rigor, breakthrough discoveries.
EXCLUDE: Speculative theories, press release science, correlation-only studies.

DO NOT include conversational framing. Output bullet list directly.""",
        max_items=4,
    ),

    Section(
        name="Automotive",
        type="rss",
        schedule=["thursday"],
        feeds=[
            FeedSource("Car and Driver", "https://caranddriver.com/rss/all.xml", priority=1),
            FeedSource("Jalopnik", "https://jalopnik.com/rss", priority=2),
        ],
        summary_prompt="""Extract 2-3 most significant stories about vehicles and technology. Output ONLY the formatted list.

REQUIRED FORMAT:
• **Vehicle/Technology**: What's new in design, engineering, or development. (https://source-url.com)

CRITICAL: Include full URL.

FOCUS ON:
- New vehicle releases (cars and motorcycles)
- EV technology advances
- Autonomous driving developments
- Design principles and concept cars
- Manufacturing innovations
- International automotive trends

EXCLUDE: Industry business news, executive moves, sales figures, exotic/supercar hype.

DO NOT include conversational framing. Output bullet list directly.""",
        max_items=3,
    ),

    Section(
        name="Design Principles",
        type="perplexity",
        schedule=["thursday"],
        search_prompt="""Search for new insights on design principles and methodology.

FOCUS ON:
- Foundational design principles being developed
- Cross-disciplinary design thinking
- Design methodology innovations
- Case studies of excellent design

Provide 2-3 paragraphs with practical insights.""",
    ),

    # ========== FRIDAY SECTIONS ==========

    Section(
        name="Politics",
        type="rss",
        schedule=["friday"],
        feeds=[
            FeedSource("NPR Politics", "https://feeds.npr.org/1014/rss.xml", priority=1),
            FeedSource("Google News Politics", "https://news.google.com/rss/search?q=politics+US&hl=en-US&gl=US&ceid=US:en", priority=2),
        ],
        summary_prompt="""Extract 2-3 most significant policy developments. Output ONLY the formatted list.

REQUIRED FORMAT:
• **Policy Development**: Impact and implications. (https://source-url.com)

CRITICAL: Include full URL.

FOCUS ON: Policy changes with real-world impact, not election horse-race.
INCLUDE: Context on implications and affected populations.

DO NOT include conversational framing. Output bullet list directly.""",
        max_items=3,
    ),

    Section(
        name="Hacker News Top Stories",
        type="rss",
        schedule=["friday"],
        feeds=[
            FeedSource("Hacker News", "https://news.ycombinator.com/rss", priority=1, max_items=20),
        ],
        summary_prompt="""Extract the 5 most technically substantive or intellectually interesting stories. Output ONLY the formatted list.

REQUIRED FORMAT:
• **Story Title**: Why it matters technically or intellectually. (https://source-url.com)

CRITICAL: Include full URL.

PRIORITIZE:
- Systems programming and architecture
- Novel technical implementations
- Academic research with practical implications
- Tools that solve real problems
- Intellectual depth over hype

SKIP: Politics, social media drama, crypto speculation.

DO NOT include conversational framing. Output bullet list directly.""",
        max_items=5,
    ),

    Section(
        name="Week in Review",
        type="perplexity",
        schedule=["friday"],
        search_prompt="""Search for the top 5-7 most significant stories from the past week (Monday-Friday).

PRIORITIZE:
- Major global developments with lasting impact
- Scientific breakthroughs and discoveries
- Significant policy changes affecting large populations
- Technical innovations with practical implications
- Cultural and intellectual developments

EXCLUDE: Celebrity news, sports (except Harvard/Colby/Tulane/Charleston), clickbait, speculative theories.

INCLUDE: Evidence-based reporting, academic rigor, context on why each story matters.

Provide comprehensive summary with 2-3 paragraphs per major story, organized by domain (global affairs, science, technology, culture).""",
    ),

    # ========== SATURDAY SECTIONS ==========

    Section(
        name="Classical Music",
        type="rss",
        schedule=["saturday"],
        feeds=[
            FeedSource("Slipped Disc", "https://slippedisc.com/feed", priority=1),
            FeedSource("Gramophone", "https://www.gramophone.co.uk/feed", priority=2),
        ],
        summary_prompt="""Extract notable stories focusing on contemporary and living composers. Output ONLY the formatted list.

REQUIRED FORMAT:
• **Composer/Event**: What's new and why it matters to contemporary music. (https://source-url.com)

CRITICAL: Include full URL.

PRIORITIZE:
- Living composers and new compositions
- World premieres and commissions
- Contemporary music festivals and ensembles
- Doctoral programs and emerging composers
- Organizations performing new works

DEPRIORITIZE: Standard repertoire performances, traditional orchestra news unless significant.

DO NOT include conversational framing. Output bullet list directly.""",
        max_items=4,
    ),

    Section(
        name="Cultural Events",
        type="perplexity",
        schedule=["saturday", "sunday"],
        search_prompt="""Search for upcoming events in next 2 weeks within 50 miles of Old Lyme, CT:
- Classical music concerts (contemporary repertoire preferred)
- Half marathons and triathlons
- Cultural festivals and exhibitions
- Notable performances

Format as bullet points with venue, date, and brief description.""",
    ),

    # ========== SUNDAY SECTIONS ==========

    Section(
        name="Media Perspectives Roundup",
        type="perplexity",
        schedule=["sunday"],
        search_prompt="""Compare and contrast how liberal-leaning and conservative-leaning news outlets covered the top 3-4 stories from the past week.

SOURCES TO COMPARE:
Liberal: NPR, New York Times, Washington Post, CNN, MSNBC
Conservative: Fox News, Wall Street Journal opinion, National Review, The Federalist

For each major story:
1. Identify the story/issue
2. Summarize liberal media framing and key talking points
3. Summarize conservative media framing and key talking points
4. Note substantive factual differences (if any)
5. Highlight where outlets agree vs where they diverge

FOCUS ON: Policy, governance, major events (not opinion shows or punditry)
TONE: Neutral, analytical, fact-based comparison

Provide 2-3 paragraphs per story with clear attribution to specific outlets.""",
    ),
]


# Helper functions
def get_sections_for_day(day_of_week: str) -> list[Section]:
    """Get all sections scheduled for a specific day"""
    return [
        section for section in SECTION_REGISTRY
        if "daily" in section.schedule or day_of_week in section.schedule
    ]


def get_section_by_name(section_name: str) -> Optional[Section]:
    """Get section configuration by name"""
    for section in SECTION_REGISTRY:
        if section.name == section_name:
            return section
    return None


# ========== COMPATIBILITY LAYER FOR OLD RSS_PARSER ==========

@dataclass
class SectionConfig:
    """Legacy configuration format for backwards compatibility"""
    feeds: list[FeedSource]
    use_llm_summary: bool = True
    use_perplexity_augment: bool = False
    summary_prompt: Optional[str] = None
    max_items: int = 5


def get_section_config(section_name: str) -> Optional[SectionConfig]:
    """Get legacy SectionConfig for a section (for backwards compatibility)"""
    section = get_section_by_name(section_name)
    if not section or section.type != "rss":
        return None

    return SectionConfig(
        feeds=section.feeds,
        use_llm_summary=True,
        use_perplexity_augment=False,
        summary_prompt=section.summary_prompt,
        max_items=section.max_items
    )
