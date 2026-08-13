import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from wiki.models import Page, Tag


class Command(BaseCommand):
    help = "Assign existing tags randomly to the 40 latest posts, with at most 3 tags per post"

    def handle(self, *args, **options):
        now = timezone.now()
        pages = (
            Page.objects.filter(
                pubdate__isnull=False,
                pubdate__lte=now,
            )
            .order_by("-pubdate")[:40]
        )
        tags = list(Tag.objects.all())

        if not tags:
            self.stdout.write(self.style.ERROR("No tags exist. Run seed_tags first."))
            return

        for page in pages:
            n = random.randint(1, min(3, len(tags)))
            assigned = random.sample(tags, n)
            page.tags.set(assigned)
            tag_list = ", ".join(t.name for t in assigned)
            self.stdout.write(f"  {page.slug}: {tag_list}")

        self.stdout.write(
            self.style.SUCCESS(f"Assigned tags to {pages.count()} pages")
        )
