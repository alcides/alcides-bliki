"""Plain-text excerpts for link previews."""

from html.parser import HTMLParser

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
