"""Markdown filter with footnotes extra and a bleach allowlist that keeps them."""

from typing import Any, ClassVar

from django_markup.filter.markdown_filter import MarkdownMarkupFilter


# Stock django-markup bleach allowlist, plus:
# - python-markdown footnotes (div.footnote, a.footnote-ref class/rel)
# - span.caps (legacy HTML kept in page source)
# - raw HTML embeds (iframe/object/embed/param/video)
# - tables kept as HTML (table/thead/tbody/tr/th/td)
# - gist/imgur/instagram script src= loaders
_MARKDOWN_TAGS = [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "b", "i", "strong", "em", "tt",
    "p", "br",
    "span", "div", "blockquote", "pre", "code", "hr",
    "ul", "ol", "li", "dd", "dt",
    "img",
    "a",
    "sub", "sup",
    "iframe", "object", "embed", "param", "video", "audio", "source",
    "table", "thead", "tbody", "tfoot", "tr", "th", "td", "caption",
    "script",
    "style",
]

_IFRAME_ATTRS = {
    "src", "width", "height", "frameborder", "allow", "allowfullscreen",
    "title", "scrolling", "class", "name", "referrerpolicy",
    "marginwidth", "marginheight", "allowtransparency",
    "webkitallowfullscreen", "mozallowfullscreen", "loading",
}

_OBJECT_ATTRS = {
    "classid", "codebase", "data", "type", "width", "height", "class",
    "name", "align", "archive",
}

_EMBED_ATTRS = {
    "src", "type", "width", "height", "class", "name", "quality", "wmode",
    "flashvars", "pluginspage", "allowfullscreen", "allowscriptaccess",
    "bgcolor", "scale", "align", "menu", "play", "loop", "title",
}

_ATTRS_BY_TAG = {
    "img": {"src", "alt", "title", "class", "width", "height"},
    "a": {"href", "alt", "title", "class", "rel"},
    "div": {"class"},
    "span": {"class", "title"},
    "iframe": _IFRAME_ATTRS,
    "object": _OBJECT_ATTRS,
    "embed": _EMBED_ATTRS,
    "param": {"name", "value", "valuetype", "type"},
    "video": {
        "src", "width", "height", "controls", "autoplay", "loop", "muted",
        "poster", "preload", "class",
    },
    "audio": {
        "src", "controls", "autoplay", "loop", "muted", "preload", "class",
    },
    "source": {"src", "type"},
    "table": {"class", "width", "height", "border", "cellpadding", "cellspacing", "align"},
    "thead": {"class", "align"},
    "tbody": {"class", "align"},
    "tfoot": {"class", "align"},
    "tr": {"class", "align", "valign"},
    "th": {
        "class", "colspan", "rowspan", "width", "height", "align", "valign",
        "scope",
    },
    "td": {
        "class", "colspan", "rowspan", "width", "height", "align", "valign",
    },
    "caption": {"class", "align"},
    "script": {"src", "type", "charset", "language", "async", "defer"},
    "style": {"type"},
    "ul": {"class"},
    "ol": {"class"},
    "li": {"class"},
}

# http/https/mailto only — javascript: and data: URLs are dropped on src/href.
_MARKDOWN_PROTOCOLS = ["http", "https", "mailto"]


def _markdown_attrs(tag, name, value):
    """Bleach attribute allowlist callable."""
    name = (name or "").lower()
    if name == "id":
        return True
    if name in _ATTRS_BY_TAG.get(tag, ()):
        return True
    # Twitter (and similar) widget iframes store data-* hooks.
    if tag == "iframe" and name.startswith("data-"):
        return True
    return False


class WikiMarkdownMarkupFilter(MarkdownMarkupFilter):
    """Stock markdown filter with a footnote- and embed-aware bleach allowlist.

    Extensions (footnotes, fenced_code) are supplied via MARKUP_SETTINGS so django-markup
    passes them into markdown(). Bleach tags/attrs cannot be configured that
    way — they are hardcoded in django-markup — so this subclass keeps class
    (and rel) on the markup python-markdown footnotes emit, plus raw HTML
    embeds/tables kept in Markdown source.
    """

    title = "Markdown"
    kwargs: ClassVar = {"safe_mode": True}

    def render(
        self,
        text: str,
        **kwargs: Any,
    ) -> str:
        if kwargs:
            self.kwargs.update(kwargs)

        from markdown import markdown

        text = markdown(text, **self.kwargs)

        if self.kwargs.get("safe_mode") is True:
            from bleach import clean

            text = clean(
                text,
                tags=_MARKDOWN_TAGS,
                attributes=_markdown_attrs,
                protocols=_MARKDOWN_PROTOCOLS,
            )

        return text
