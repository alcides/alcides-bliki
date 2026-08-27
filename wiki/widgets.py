from django.contrib.admin.widgets import AdminTextareaWidget
from django.urls import reverse


class AdminMarkdownPreviewWidget(AdminTextareaWidget):
    """Admin textarea with a live Markdown preview pane."""

    template_name = "admin/wiki/widgets/markdown_preview.html"

    class Media:
        js = ("wiki/admin/markdown_preview.js",)
        css = {"all": ("wiki/admin/markdown_preview.css",)}

    def get_context(self, name, value, attrs):
        context = super(AdminMarkdownPreviewWidget, self).get_context(
            name, value, attrs
        )
        context["preview_url"] = reverse("admin:wiki_page_markdown_preview")
        return context
