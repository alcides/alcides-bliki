(function () {
  var quote = (window.getSelection() ? window.getSelection().toString() : "").replace(/^\s+|\s+$/g, "");
  var title = document.title || "";
  var url = location.href;
  var author = "";
  var authorUrl = "";
  var i;
  var el;
  var content;
  var links;
  var href;
  var text;
  var metas = [
    'meta[name="author"]',
    'meta[property="article:author"]',
    'meta[name="citation_author"]',
    'meta[property="og:article:author"]',
    'meta[name="byl"]',
    'meta[name="twitter:creator"]'
  ];
  for (i = 0; i < metas.length; i += 1) {
    el = document.querySelector(metas[i]);
    if (!el) {
      continue;
    }
    content = (el.getAttribute("content") || "").replace(/^\s+|\s+$/g, "");
    if (!content) {
      continue;
    }
    if (content.charAt(0) === "@" && !author) {
      author = content.slice(1);
      continue;
    }
    if (/^https?:\/\//i.test(content)) {
      if (!authorUrl) {
        authorUrl = content;
      }
      continue;
    }
    if (!author) {
      author = content;
    }
  }
  el = document.querySelector('a[rel="author"], [itemprop="author"] a');
  if (el) {
    text = (el.textContent || "").replace(/^\s+|\s+$/g, "");
    href = el.href || "";
    if (text && !author) {
      author = text;
    }
    if (href && !authorUrl) {
      authorUrl = href;
    }
  }
  if (author && !authorUrl) {
    links = document.getElementsByTagName("a");
    for (i = 0; i < links.length; i += 1) {
      text = (links[i].textContent || "").replace(/^\s+|\s+$/g, "");
      if (text === author && links[i].href) {
        authorUrl = links[i].href;
        break;
      }
    }
  }
  window.open(
    "__ADD_URL__#bm=" + encodeURIComponent(JSON.stringify({
      t: title,
      u: url,
      q: quote,
      a: author,
      au: authorUrl
    })),
    "_blank"
  );
})();
