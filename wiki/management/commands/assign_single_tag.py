"""
Assign each page to the single most likely tag based on content analysis.
Reads title, slug, and text and scores each tag by keyword relevance.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from wiki.models import Page, Tag


TAG_NAMES = [
    "Software Engineering",
    "Academia",
    "Research",
    "Politics",
    "Music",
    "Movies",
    "Boardgames",
    "Technology",
]

# Keywords (lowercase) that suggest a tag. Longer/more specific keywords first.
TAG_KEYWORDS = {
    "Software Engineering": [
        "software engineering", "programming language", "code review", "codebase",
        "algorithm", "api", "python", "javascript", "rust", "haskell", "ocaml",
        "compiler", "debugging", "refactoring", "microservices", "open source",
        "opensource", "github", "git", "docker", "flask", "django", "testing",
        "software", "engineering", "code", "programming", "development", "developer",
        "web app", "webapp", "implementation", "syntax", "function", "class",
    ],
    "Academia": [
        "phd", "dissertation", "thesis", "professor", "faculty", "lecture",
        "curriculum", "syllabus", "student", "graduate", "undergraduate",
        "academia", "academic", "teaching", "university", "universidade",
        "course", "lecture", "seminar", "workshop", "caloiro", "propinas",
    ],
    "Research": [
        "research", "paper", "publication", "citation", "peer review",
        "experiment", "study", "findings", "methodology", "pldi", "oopsla",
        "conference paper", "journal", "scientific", "empirical",
    ],
    "Politics": [
        "election", "government", "democracy", "regulation", "law",
        "politics", "political", "parliament", "minister", "trudeau",
        "autarquicas", "greves", "estatuto", "carreira cientifica",
    ],
    "Music": [
        "album", "band", "concert", "guitar", "piano", "song", "track",
        "music", "musical", "wrapped", "2024 in music", "2025 in music",
        "power metal", "blue man group", "ghost of corporate future",
    ],
    "Movies": [
        "movie", "film", "cinema", "actor", "director", "wargames",
        "ironman", "kungfupanda", "screen", "trailer", "watching millionaires",
    ],
    "Boardgames": [
        "boardgame", "board game", "boardgames", "tabletop", "hexagonal",
        "dice", "card game", "uno rules", "the-world-is-an-hexagonal",
    ],
    "Technology": [
        "technology", "tech", "computer", "digital", "internet", "data",
        "ai", "llm", "machine learning", "neural", "chatgpt",
    ],
}

# Tag preference when scores are tied (more specific first)
TAG_PRIORITY = [
    "Boardgames", "Music", "Movies", "Politics", "Research", "Academia",
    "Software Engineering", "Technology",
]


def score_tag(content_lower: str, title_lower: str, slug_lower: str, tag_name: str) -> float:
    """Score how well a tag matches the content. Higher = better match."""
    keywords = TAG_KEYWORDS.get(tag_name, [])
    score = 0.0
    for kw in keywords:
        if kw in content_lower:
            # Base score from full content
            count = content_lower.count(kw)
            score += count * 1.0
            # Boost if in title (strong signal)
            if kw in title_lower:
                score += 5.0
            # Boost if in slug (very strong signal)
            if kw in slug_lower:
                score += 10.0
    return score


class Command(BaseCommand):
    help = "Assign each page to the single most likely tag based on content"

    def handle(self, *args, **options):
        tag_objs = {}
        for name in TAG_NAMES:
            slug = slugify(name)
            tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
            tag_objs[name] = tag

        pages = Page.objects.all()
        for page in pages:
            title = str(page.title or "").lower()
            slug = str(page.slug or "").lower()
            text = str(page.text or "").lower()
            content = f"{title} {slug} {text}"

            best_tag_name = None
            best_score = -1.0

            for tag_name in TAG_PRIORITY:
                s = score_tag(content, title, slug, tag_name)
                if s > best_score:
                    best_score = s
                    best_tag_name = tag_name

            if best_tag_name is None or best_score <= 0:
                best_tag_name = "Technology"

            page.tags.set([tag_objs[best_tag_name]])
            self.stdout.write(f"  {page.slug}: {best_tag_name}")

        self.stdout.write(self.style.SUCCESS(f"Assigned single tag to {pages.count()} pages"))
