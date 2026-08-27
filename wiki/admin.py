from datetime import datetime

from django.contrib import admin
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.text import slugify
from django.utils import timezone
from django_markup.templatetags.markup_tags import apply_markup

from wiki.models import ImageUpload, Language, Page, PageVersion, Tag
from wiki.widgets import AdminMarkdownPreviewWidget


def publish(modeladmin, req, qs):
    qs.update(pubdate=datetime.now())


def _md_link(label, href):
    label = (label or "").replace("[", "\\[").replace("]", "\\]")
    return "[%s](%s)" % (label, href)


def bookmarklet_markdown(title, url, quote, source_author="", source_author_url=""):
    attrib = "— %s" % _md_link(title, url)
    if source_author:
        if source_author_url:
            attrib += " by %s" % _md_link(source_author, source_author_url)
        else:
            attrib += " by %s" % source_author
    parts = []
    if quote:
        quoted = "\n".join(
            "> %s" % line
            for line in quote.replace("\r\n", "\n").split("\n")
        )
        parts.append(quoted)
    parts.append(attrib)
    return "\n\n".join(parts) + "\n\n"


class TagAdmin(admin.ModelAdmin):
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


class PageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["slug", "title", "text"]
    list_filter = ("lang", "pubdate", "date", "author")
    list_display = (
        "title",
        "slug",
        "is_published",
        "date",
        "lang",
        "get_tags_display",
    )
    list_display_links = ("title", "slug")
    autocomplete_fields = ["tags"]

    class Media:
        js = (
            "wiki/admin/markdown_preview.js",
            "wiki/admin/bookmarklet_prefill.js",
        )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("tags")

    @admin.display(description="Tags")
    def get_tags_display(self, obj):
        return ", ".join(t.name for t in obj.tags.all())

    fieldsets = (
        ("Content", {"fields": ("title", "text")}),
        ("Meta", {"fields": ("slug", "lang", "pubdate", "author", "tags")}),
    )

    save_on_top = True
    actions = [publish]

    def get_urls(self):
        urls = super().get_urls()
        extra = [
            path(
                "markdown-preview/",
                self.admin_site.admin_view(self.markdown_preview_view),
                name="wiki_page_markdown_preview",
            ),
            path(
                "quote-bookmarklet/",
                self.admin_site.admin_view(self.quote_bookmarklet_view),
                name="wiki_page_quote_bookmarklet",
            ),
        ]
        return extra + urls

    def markdown_preview_view(self, request):
        if request.method != "POST":
            return JsonResponse({"html": ""}, status=405)
        text = request.POST.get("text", "")
        html = apply_markup(text, "markdown")
        return JsonResponse({"html": str(html)})

    def quote_bookmarklet_view(self, request):
        add_url = request.build_absolute_uri(reverse("admin:wiki_page_add"))
        js_path = "wiki/static/wiki/admin/quote_bookmarklet.js"
        import os

        path = os.path.join(os.path.dirname(__file__), "static/wiki/admin/quote_bookmarklet.js")
        with open(path) as fh:
            body = fh.read().replace("__ADD_URL__", add_url)
        # Minify to a single javascript: URL.
        compact = " ".join(line.strip() for line in body.splitlines() if line.strip())
        bookmarklet = "javascript:" + compact
        return render(
            request,
            "admin/wiki/page/bookmarklet.html",
            {"bookmarklet": bookmarklet},
        )

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        title = request.GET.get("title")
        url = request.GET.get("url")
        if not title and not url and "quote" not in request.GET:
            return initial
        title = title or ""
        url = url or ""
        quote = request.GET.get("quote", "")
        source_author = request.GET.get("source_author", "")
        source_author_url = request.GET.get("source_author_url", "")
        initial["title"] = title[:180]
        initial["text"] = bookmarklet_markdown(
            title, url, quote, source_author, source_author_url
        )
        slug = "blog/%s" % (slugify(title) or "post")
        initial["slug"] = slug[:60]
        initial["pubdate"] = timezone.now()
        first_user = User.objects.order_by("pk").first()
        if first_user:
            initial["author"] = first_user.pk
        first_lang = Language.objects.order_by("pk").first()
        if first_lang:
            initial["lang"] = first_lang.pk
        return initial

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "text":
            kwargs["widget"] = AdminMarkdownPreviewWidget(attrs={"rows": 24})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


def restore_version(modeladmin, req, qs):
    for o in qs:
        p = o.page
        p.text = o.text
        p.save()


class PageVersionAdmin(admin.ModelAdmin):
    list_display = ("page", "version")
    actions = [restore_version]


admin.site.register(Language)
admin.site.register(Tag, TagAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(PageVersion, PageVersionAdmin)
admin.site.register(ImageUpload)
