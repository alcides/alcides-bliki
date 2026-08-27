(function () {
  "use strict";

  function parsePayload() {
    var hash = location.hash || "";
    if (hash.indexOf("#bm=") === 0) {
      try {
        return JSON.parse(decodeURIComponent(hash.slice(4)));
      } catch (err) {
        return null;
      }
    }
    return null;
  }

  function mdLink(label, href) {
    var text = String(label || "").replace(/\[/g, "\\[").replace(/\]/g, "\\]");
    return "[" + text + "](" + href + ")";
  }

  function asQuote(value) {
    var lines = String(value).replace(/\r\n/g, "\n").split("\n");
    var out = [];
    var i;
    for (i = 0; i < lines.length; i += 1) {
      out.push("> " + lines[i]);
    }
    return out.join("\n");
  }

  function slugify(value) {
    return String(value)
      .toLowerCase()
      .replace(/['\u2019]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 54);
  }

  function pad(n) {
    return n < 10 ? "0" + n : String(n);
  }

  function setFirstChoice(sel) {
    var i;
    if (!sel || sel.value) {
      return;
    }
    for (i = 0; i < sel.options.length; i += 1) {
      if (sel.options[i].value) {
        sel.selectedIndex = i;
        return;
      }
    }
  }

  function apply(data) {
    var title = data.t || "";
    var url = data.u || "";
    var quote = data.q || "";
    var author = data.a || "";
    var authorUrl = data.au || "";
    var titleField = document.getElementById("id_title");
    var textField = document.getElementById("id_text");
    var slugField = document.getElementById("id_slug");
    var dateField = document.getElementById("id_pubdate_0");
    var timeField = document.getElementById("id_pubdate_1");
    var now = new Date();
    var attrib = "— " + mdLink(title, url);
    var body = "";
    var slug;

    if (!titleField || !textField) {
      return;
    }
    if (author) {
      attrib += " by " + (authorUrl ? mdLink(author, authorUrl) : author);
    }
    if (quote) {
      body = asQuote(quote) + "\n\n";
    }
    body += attrib + "\n\n";

    if (!titleField.value) {
      titleField.value = title.slice(0, 180);
    }
    if (!textField.value) {
      textField.value = body;
    }
    slug = "blog/" + (slugify(title) || "post");
    if (slugField && !slugField.value) {
      slugField.value = slug.slice(0, 60);
    }
    if (dateField && !dateField.value) {
      dateField.value =
        now.getFullYear() +
        "-" +
        pad(now.getMonth() + 1) +
        "-" +
        pad(now.getDate());
    }
    if (timeField && !timeField.value) {
      timeField.value =
        pad(now.getHours()) +
        ":" +
        pad(now.getMinutes()) +
        ":" +
        pad(now.getSeconds());
    }
    setFirstChoice(document.getElementById("id_author"));
    setFirstChoice(document.getElementById("id_lang"));
    if (textField.dispatchEvent) {
      textField.dispatchEvent(new Event("input", { bubbles: true }));
    }
  }

  function init() {
    var data;
    if (!/\/admin\/wiki\/page\/add\/?$/.test(location.pathname)) {
      return;
    }
    data = parsePayload();
    if (!data) {
      return;
    }
    apply(data);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
