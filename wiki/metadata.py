"""Text and image metadata for link previews."""

from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from django.conf import settings
from django.utils.encoding import iri_to_uri
from django.utils.text import Truncator
from django_markup.templatetags.markup_tags import apply_markup


class _PreviewText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1
        if tag in {"p", "br", "div", "li", "blockquote", "pre", "hr",
                   "h1", "h2", "h3", "h4", "h5", "h6", "td", "th"}:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.hidden:
            self.hidden -= 1
        if tag in {"p", "div", "li", "blockquote", "pre",
                   "h1", "h2", "h3", "h4", "h5", "h6", "td", "th"}:
            self.parts.append(" ")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def preview_description(text):
    parser = _PreviewText()
    parser.feed(str(apply_markup(text, "markdown")))
    parser.close()
    return Truncator(" ".join("".join(parser.parts).split())).chars(160)


class _PreviewImages(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.images.append(dict(attrs))


def preview_image(text, page_url):
    """Find the first rendered image with a usable HTTP(S) source."""
    parser = _PreviewImages()
    parser.feed(str(apply_markup(text, "markdown")))
    parser.close()
    for image in parser.images:
        source = (image.get("src") or "").strip()
        if not source:
            continue
        try:
            url = urljoin(page_url, source)
            parsed = urlsplit(url)
            if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                continue
        except ValueError:
            continue
        return {"url": iri_to_uri(url), "alt": image.get("alt") or ""}
    return None


def default_preview_image(request):
    return {
        "url": request.build_absolute_uri(urljoin(settings.MEDIA_URL, "images/alcides_fonseca.jpg")),
        "alt": "Alcides Fonseca",
    }
