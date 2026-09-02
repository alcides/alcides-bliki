"""Markdown filter with footnotes extra and a bleach allowlist that keeps them."""

from typing import Any, ClassVar
from urllib.parse import urlsplit, urlunsplit

from bleach.html5lib_shim import Filter
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


# Amazon Associates tracking IDs, appended to Amazon shopping links at render
# time so the stored page corpus never needs rewriting and future posts pick
# them up automatically. Tracking IDs are per-locale; only locales with a
# registered ID are tagged. Other Amazon shopping locales (amazon.de,
# amazon.co.uk, ...) are left untouched — tagging them with a US/ES ID would
# not credit anything.
#
# Keys are registrable domains of Amazon retail (shopping) sites. Only the
# bare domain and the www./smile. subdomains are tagged, which automatically
# excludes non-shopping properties (aws.amazon.com, developer.amazon.com,
# music.amazon.*, alexa.amazon.*, astore.amazon.com, ...) as well as
# amazon.jobs and *.amazonaws.com.
#
# Short links (amzn.to, a.co, amzn.eu) are deliberately left alone: they are
# opaque redirects, and appending tag= to the short URL is discarded during
# the redirect, so tagging them without expanding the link is useless.
# Legacy astore.amazon.com iframes are also left alone — aStores were retired
# in 2017 and the embeds are dead either way.
AMAZON_AFFILIATE_TAGS = {
    "amazon.com": "alcidesfonsec-20",
    "amazon.es": "alcidesfonsec-21",
}

_AMAZON_HOST_PREFIXES = ("", "www.", "smile.")


def _amazon_affiliate_tag_for_host(hostname):
    """Return the tracking ID for an Amazon shopping host, or None."""
    hostname = (hostname or "").lower().rstrip(".")
    for prefix in _AMAZON_HOST_PREFIXES:
        if hostname.startswith(prefix):
            tag = AMAZON_AFFILIATE_TAGS.get(hostname[len(prefix):])
            if tag is not None:
                return tag
    return None


def _tag_amazon_url(url):
    """Return url with the locale's tag= if it is a tagged Amazon shopping URL.

    Any existing tag= parameter is replaced; everything else in the URL
    (path, other query params, fragment) is preserved byte-for-byte.
    Non-Amazon URLs, non-shopping Amazon URLs, and shopping locales without
    a registered tracking ID are returned unchanged.
    """
    try:
        parts = urlsplit(url)
    except ValueError:
        return url
    # scheme == "" covers protocol-relative //www.amazon.com/... URLs.
    if parts.scheme not in ("http", "https", ""):
        return url
    tag = _amazon_affiliate_tag_for_host(parts.hostname)
    if tag is None:
        return url
    # Bleach's tokenizer keeps character entities in attribute values as-is,
    # so param separators may arrive as "&amp;". Normalize just that sequence
    # (the serializer re-escapes bare "&" on output) so tag= is detected.
    query = parts.query.replace("&amp;", "&")
    params = [
        param for param in query.split("&")
        if param and param.split("=", 1)[0] != "tag"
    ]
    params.append("tag=" + tag)
    return urlunsplit(parts._replace(query="&".join(params)))


class AmazonAffiliateFilter(Filter):
    """html5lib filter that tags Amazon shopping links during bleach cleaning.

    Runs inside bleach's Cleaner *after* sanitizing, so javascript:/data:
    URLs are already gone before rewriting, and the serializer keeps
    attribute escaping correct. It only rewrites the URL value of existing
    href/src attributes, never injecting tags or attributes, so the bleach
    security allowlist is unchanged.
    """

    def __iter__(self):
        for token in super().__iter__():
            if token.get("type") in ("StartTag", "EmptyTag") and token.get("name") in ("a", "iframe"):
                data = token.get("data") or {}
                key = (None, "href" if token["name"] == "a" else "src")
                if data.get(key):
                    data[key] = _tag_amazon_url(data[key])
            yield token


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
            from bleach.sanitizer import Cleaner

            cleaner = Cleaner(
                tags=_MARKDOWN_TAGS,
                attributes=_markdown_attrs,
                protocols=_MARKDOWN_PROTOCOLS,
                filters=[AmazonAffiliateFilter],
            )
            text = cleaner.clean(text)

        return text
