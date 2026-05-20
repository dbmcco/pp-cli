#!/Users/braydon/projects/experiments/pp/scripts/venv/bin/python3

# ABOUTME: RSS feed configuration for morning briefing sections
# ABOUTME: Maps briefing sections to curated, authoritative RSS sources

from dataclasses import dataclass
from typing import Optional

@dataclass
class FeedSource:
    """Single RSS feed source with metadata"""
    name: str
    url: str
    priority: int = 1  # Lower = higher priority for deduplication
    max_items: int = 10


@dataclass
class SectionConfig:
    """Configuration for a briefing section"""
    feeds: list[FeedSource]
    use_llm_summary: bool = True
    use_perplexity_augment: bool = False
    summary_prompt: Optional[str] = None
    max_items: int = 5


# Feed definitions organized by briefing section
SECTION_FEEDS: dict[str, SectionConfig] = {

    "Key Headlines": SectionConfig(
        feeds=[
            FeedSource("Google News", "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en", priority=1),
            FeedSource("NPR Top Stories", "https://feeds.npr.org/1001/rss.xml", priority=2),
            FeedSource("BBC News", "http://feeds.bbci.co.uk/news/rss.xml", priority=3),
        ],
        use_llm_summary=True,
        summary_prompt="""Select the 3-5 most important global news stories from the past 48 hours only.

EXCLUDE: Celebrity/entertainment, sports, true crime, lifestyle trends.
PRIORITIZE: Breaking news, major policy developments, significant global events.

Format each as: • **Headline**: Brief summary with source attribution.""",
        max_items=5,
    ),

    "Tech & AI": SectionConfig(
        feeds=[
            FeedSource("Hacker News", "https://news.ycombinator.com/rss", priority=1, max_items=15),
            FeedSource("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index", priority=2),
            FeedSource("The Verge", "https://theverge.com/rss/index.xml", priority=3),
            FeedSource("TechCrunch", "https://techcrunch.com/feed", priority=4),
        ],
        use_llm_summary=True,
        use_perplexity_augment=False,  # Deep dive handles this
        summary_prompt="""Identify 3-5 most significant stories for systems builders and AI integrators.

FOCUS ON:
- CLI tools and frameworks
- AI integration patterns (MCP servers, agent architectures)
- Developer tools and workflows
- Technical implementations (not announcements)
- Open source projects with substance

EXCLUDE: Funding rounds, executive moves, generic AI ethics, industry drama.

Format each as: • **Tool/Project Name**: What it does and why it matters technically.""",
        max_items=5,
    ),

    "Hacker News Top Stories": SectionConfig(
        feeds=[
            FeedSource("Hacker News", "https://news.ycombinator.com/rss", priority=1, max_items=20),
        ],
        use_llm_summary=True,
        summary_prompt="""Select the 5 most technically substantive or intellectually interesting stories.

PRIORITIZE:
- Systems programming and architecture
- Novel technical implementations
- Academic research with practical implications
- Tools that solve real problems
- Intellectual depth over hype

SKIP: Politics, social media drama, crypto speculation.

Format each as: • **Story Title**: Why it matters technically or intellectually.""",
        max_items=5,
    ),

    "Connecticut": SectionConfig(
        feeds=[
            FeedSource("CT Mirror", "https://ctmirror.org/feed", priority=1),
            # CT Public feed has XML parsing issues, skipping
            FeedSource("Hartford Courant", "https://courant.com/feed", priority=2),
            FeedSource("CT News Junkie", "https://ctnewsjunkie.com/feed/", priority=3),
        ],
        use_llm_summary=True,
        summary_prompt="""From these Connecticut news items, select 2-3 most relevant stories.
Prioritize: state politics, local events, community news affecting shoreline/Old Lyme area.
Format as bullet points: • **Headline**: Brief summary with location context.""",
        max_items=3,
    ),

    "Classical Music": SectionConfig(
        feeds=[
            FeedSource("Slipped Disc", "https://slippedisc.com/feed", priority=1),
            # I Care If You Listen feed often empty, using Gramophone instead
            FeedSource("Gramophone", "https://www.gramophone.co.uk/feed", priority=2),
        ],
        use_llm_summary=True,
        use_perplexity_augment=False,  # Deep dive handles concert listings
        summary_prompt="""Select notable stories focusing on contemporary and living composers.

PRIORITIZE:
- Living composers and new compositions
- World premieres and commissions
- Contemporary music festivals and ensembles
- Doctoral programs and emerging composers
- Organizations performing new works

DEPRIORITIZE: Standard repertoire performances, traditional orchestra news unless significant.

Format each as: • **Composer/Event**: What's new and why it matters to contemporary music.""",
        max_items=4,
    ),

    "Automotive": SectionConfig(
        feeds=[
            FeedSource("Car and Driver", "https://caranddriver.com/rss/all.xml", priority=1),
            FeedSource("Jalopnik", "https://jalopnik.com/rss", priority=2),
        ],
        use_llm_summary=True,
        summary_prompt="""Select 2-3 most significant stories about vehicles and technology.

FOCUS ON:
- New vehicle releases (cars and motorcycles)
- EV technology advances
- Autonomous driving developments
- Design principles and concept cars
- Manufacturing innovations
- International automotive trends

EXCLUDE: Industry business news, executive moves, sales figures, exotic/supercar hype.

Format each as: • **Vehicle/Technology**: What's new in design, engineering, or development.""",
        max_items=3,
    ),

    "Politics": SectionConfig(
        feeds=[
            FeedSource("NPR Politics", "https://feeds.npr.org/1014/rss.xml", priority=1),
            # Politico has SSL cert issues, using AP Politics via Google News instead
            FeedSource("Google News Politics", "https://news.google.com/rss/search?q=politics+US&hl=en-US&gl=US&ceid=US:en", priority=2),
        ],
        use_llm_summary=True,
        summary_prompt="""Select 2-3 most significant policy developments.

FOCUS ON: Policy changes with real-world impact, not election horse-race.
INCLUDE: Context on implications and affected populations.

Format each as: • **Policy Development**: Impact and implications.""",
        max_items=3,
    ),

    "Science Roundup": SectionConfig(
        feeds=[
            FeedSource("Nature News", "https://www.nature.com/nature.rss", priority=1),
            FeedSource("Science News", "https://www.sciencenews.org/feed", priority=2),
            FeedSource("Phys.org", "https://phys.org/rss-feed/", priority=3),
        ],
        use_llm_summary=True,
        summary_prompt="""Select 3-4 most significant scientific discoveries or developments.

COVERAGE: Space, medical, climate, physics, neuroscience, materials, energy, biology.
FOCUS ON: Evidence-based research, academic rigor, breakthrough discoveries.
EXCLUDE: Speculative theories, press release science, correlation-only studies.

Format each as: • **Discovery/Development**: What was found and why it matters.""",
        max_items=4,
    ),

    "Archaeological Discoveries": SectionConfig(
        feeds=[
            FeedSource("Archaeology News", "https://www.archaeology.org/feed", priority=1),
            FeedSource("Heritage Daily", "https://www.heritagedaily.com/feed", priority=2),
        ],
        use_llm_summary=True,
        summary_prompt="""Select notable archaeological findings with academic rigor.

PRIORITIZE:
- Novel early history discoveries
- Ancient technology breakthroughs
- Climate/environmental impacts on civilizations
- Lost cities and cultures
- Human migration and origins evidence

EXCLUDE: Speculative timeline rewrites, sensationalist claims.

Format each as: • **Discovery**: What was found, where, and what it reveals.""",
        max_items=2,
    ),

    "Design Innovations": SectionConfig(
        feeds=[
            FeedSource("Core77", "http://www.core77.com/posts/rss", priority=1),
            FeedSource("Dezeen", "https://www.dezeen.com/feed/", priority=2),
        ],
        use_llm_summary=True,
        summary_prompt="""Select 2-3 most innovative design developments.

FOCUS ON:
- Product/industrial design
- Architecture and urban design
- UX/interface design
- Information design and data visualization
- Service/system design
- Design principles and methodology

EXCLUDE: Pure fashion, interior decoration, graphic design.

Format each as: • **Project/Innovation**: What problem it solves and how.""",
        max_items=3,
    ),

    "Cognitive Science": SectionConfig(
        feeds=[
            FeedSource("Psychology Today", "https://www.psychologytoday.com/us/front/feed", priority=1),
            FeedSource("ScienceDaily Neuroscience", "https://www.sciencedaily.com/rss/mind_brain.xml", priority=2),
        ],
        use_llm_summary=True,
        summary_prompt="""Select academic research on creativity and intuition mechanisms.

FOCUS ON:
- How creativity functions
- Mechanisms of intuitive thought
- Cognitive processes in creative work
- Academic studies with rigor

EXCLUDE: Pop psychology, self-help, speculative theories.

Format each as: • **Research Finding**: What the study reveals about creative/intuitive processes.""",
        max_items=2,
    ),
}


# Deep dive topics that rotate by day of week (1-3 per day based on content)
DEEP_DIVE_SCHEDULE: dict[str, list[str]] = {
    "monday": ["Contemporary Music Trends", "AI Workflows & Tools", "Design Innovations"],
    "tuesday": ["Archaeological Discoveries", "Cognitive Science Research", "EV & Autonomous Tech"],
    "wednesday": ["New Music Compositions", "AI System Architecture", "Intellectual Trends"],
    "thursday": ["Materials Science & Manufacturing", "Design Principles", "Automotive Releases"],
    "friday": ["Week in Review"],  # Friday keeps week in review
    "saturday": ["Cultural Events", "Race Calendar"],
    "sunday": ["Cultural Events", "Race Calendar"],
}

# Deep dive prompts for Perplexity web search
DEEP_DIVE_PROMPTS: dict[str, str] = {
    "Contemporary Music Trends": """Search for current trends in contemporary classical music composition.

FOCUS ON:
- Post-minimalism and spectral music developments
- New compositional techniques and approaches
- Emerging composers and doctoral programs
- Contemporary music festivals and commissions
- Cross-pollination with technology (AI composition, new notation)

Provide 2-3 paragraphs with academic rigor.""",

    "AI Workflows & Tools": """Search for new CLI tools, frameworks, and integration patterns for AI systems.

FOCUS ON:
- CLI-first AI tools launched in past month
- MCP server implementations and agent frameworks
- PKM + AI workflow innovations
- Audio transcription and structured data pipelines
- Builder/developer-focused technical content

Provide 2-3 paragraphs on most significant developments.""",

    "New Music Compositions": """Search for recent world premieres, commissions, and new works by living composers.

FOCUS ON:
- Contemporary classical premieres in past month
- Organizations commissioning/performing new works
- Living composers releasing major works
- Doctoral composition programs and graduate work
- Post-minimal and spectral music specifically

Provide 2-3 paragraphs with specific works and composers.""",

    "AI System Architecture": """Search for technical articles on AI integration architectures and patterns.

FOCUS ON:
- MCP (Model Context Protocol) implementations
- Agent coordination frameworks
- Context management and memory systems
- Tool-calling architectures
- Production AI system design patterns

Provide 2-3 paragraphs with technical depth.""",

    "Cultural Events": """Search for upcoming events in next 2 weeks within 50 miles of Old Lyme, CT:
- Classical music concerts (contemporary repertoire preferred)
- Half marathons and triathlons
- Cultural festivals and exhibitions
- Notable performances

Format as bullet points with venue, date, and brief description.""",

    "Race Calendar": """Search for upcoming half marathons and triathlons within 50 miles of Old Lyme, CT in next 3 months.

Include: race name, location, date, distance, registration link if available.
Format as bullet points.""",

    "Design Innovations": """Search for recent innovative design projects and developments.

FOCUS ON:
- Product/industrial design breakthroughs
- Architectural innovations
- UX/interface design patterns
- Information design and data visualization
- Service/system design methodologies

Provide 2-3 paragraphs on most significant projects.""",

    "Archaeological Discoveries": """Search for recent archaeological discoveries and findings.

FOCUS ON:
- Novel early history discoveries
- Ancient technology breakthroughs
- Climate/environmental impacts on civilizations
- Lost cities and cultures
- Human migration evidence

Provide 2-3 paragraphs with academic sources.""",

    "Cognitive Science Research": """Search for recent research on creativity and intuition.

FOCUS ON:
- How creativity functions neurologically
- Mechanisms of intuitive thought
- Cognitive processes in creative work
- Academic studies on insight and innovation

Provide 2-3 paragraphs from peer-reviewed sources.""",

    "EV & Autonomous Tech": """Search for recent developments in electric vehicles and autonomous driving.

FOCUS ON:
- Battery technology advances
- Charging infrastructure innovations
- Autonomous driving technical progress
- Real-world testing and deployment

Provide 2-3 paragraphs with technical depth.""",

    "Intellectual Trends": """Search for emerging ideas and philosophical movements.

FOCUS ON:
- Big ideas in philosophy and social thought
- Academic discourse and new frameworks
- Intellectual movements gaining traction
- Cross-disciplinary intellectual work

Provide 2-3 paragraphs from academic sources.""",

    "Materials Science & Manufacturing": """Search for innovations in materials science and manufacturing.

FOCUS ON:
- New materials and their properties
- Manufacturing process innovations
- 3D printing and additive manufacturing
- Sustainable materials development

Provide 2-3 paragraphs with technical details.""",

    "Design Principles": """Search for new insights on design principles and methodology.

FOCUS ON:
- Foundational design principles being developed
- Cross-disciplinary design thinking
- Design methodology innovations
- Case studies of excellent design

Provide 2-3 paragraphs with practical insights.""",

    "Automotive Releases": """Search for new vehicle releases and concept cars in past month.

FOCUS ON:
- New car and motorcycle releases
- Concept cars and design previews
- International automotive market
- Design and engineering innovations

Provide 2-3 paragraphs on most significant releases.""",

    "Week in Review": """Search for the top 5-7 most significant stories from the past week (Monday-Friday).

PRIORITIZE:
- Major global developments with lasting impact
- Scientific breakthroughs and discoveries
- Significant policy changes affecting large populations
- Technical innovations with practical implications
- Cultural and intellectual developments

EXCLUDE: Celebrity news, sports (except Harvard/Colby/Tulane/Charleston), clickbait, speculative theories.

INCLUDE: Evidence-based reporting, academic rigor, context on why each story matters.

Provide comprehensive summary with 2-3 paragraphs per major story, organized by domain (global affairs, science, technology, culture).""",
}

# Perplexity augmentation prompts for regular sections
AUGMENT_PROMPTS: dict[str, str] = {}  # Removed - using DEEP_DIVE_PROMPTS instead


def get_section_config(section_name: str) -> Optional[SectionConfig]:
    """Get configuration for a section, with fuzzy matching"""
    # Exact match
    if section_name in SECTION_FEEDS:
        return SECTION_FEEDS[section_name]

    # Fuzzy match (case-insensitive, partial)
    section_lower = section_name.lower()
    for key, config in SECTION_FEEDS.items():
        if key.lower() in section_lower or section_lower in key.lower():
            return config

    return None
