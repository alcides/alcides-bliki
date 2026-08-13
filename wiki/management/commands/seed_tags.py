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

# Keywords (lowercase) that suggest a tag. A page matching any keyword gets that tag.
TAG_KEYWORDS = {
    "Software Engineering": [
        "software", "engineering", "code", "programming", "api", "python",
        "javascript", "development", "developer", "web", "app", "algorithm",
    ],
    "Academia": [
        "academia", "teaching", "university", "phd", "professor", "course",
        "lecture", "student", "thesis", "dissertation", "faculty",
    ],
    "Research": [
        "research", "paper", "study", "experiment", "publication", "citation",
    ],
    "Politics": [
        "politics", "political", "election", "government", "democracy",
    ],
    "Music": [
        "music", "album", "band", "song", "concert", "guitar", "piano",
    ],
    "Movies": [
        "movie", "film", "cinema", "actor", "director", "screen",
    ],
    "Boardgames": [
        "boardgame", "board game", "boardgames", "tabletop", "dice", "card game",
    ],
    "Technology": [
        "technology", "tech", "computer", "digital", "internet", "data",
    ],
}


class Command(BaseCommand):
    help = "Create default tags and associate each page with one or more tags"

    def handle(self, *args, **options):
        # Create tags
        tag_objs = {}
        for name in TAG_NAMES:
            slug = slugify(name)
            tag, created = Tag.objects.get_or_create(
                slug=slug,
                defaults={"name": name},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created tag: {tag.name}"))
            tag_objs[name] = tag

        # Associate pages with tags
        pages = Page.objects.all()
        for page in pages:
            content = " ".join(
                str(x or "").lower()
                for x in [page.title, page.slug, page.text]
            )
            assigned = set()
            for tag_name, keywords in TAG_KEYWORDS.items():
                if any(kw in content for kw in keywords):
                    assigned.add(tag_objs[tag_name])

            # Default to Technology if no tags matched
            if not assigned:
                assigned.add(tag_objs["Technology"])

            page.tags.set(assigned)
            tag_list = ", ".join(t.name for t in assigned)
            self.stdout.write(f"  {page.slug}: {tag_list}")

        self.stdout.write(self.style.SUCCESS(f"Associated tags with {pages.count()} pages"))
