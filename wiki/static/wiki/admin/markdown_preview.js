(function () {
  "use strict";

  var DEBOUNCE_MS = 250;

  function getCookie(name) {
    var cookies = document.cookie ? document.cookie.split(";") : [];
    var prefix = name + "=";
    var i;
    var cookie;
    for (i = 0; i < cookies.length; i += 1) {
      cookie = cookies[i].trim();
      if (cookie.indexOf(prefix) === 0) {
        return decodeURIComponent(cookie.substring(prefix.length));
      }
    }
    return "";
  }

  function renderPreview(wrapper) {
    var textarea = wrapper.querySelector("textarea");
    var output = wrapper.querySelector(".markdown-preview-output");
    var url = wrapper.getAttribute("data-preview-url");
    var token;
    var body;
    if (!textarea || !output || !url) {
      return;
    }
    if (wrapper._previewAbort) {
      wrapper._previewAbort.abort();
    }
    wrapper._previewAbort = new AbortController();
    token = getCookie("csrftoken");
    body = new URLSearchParams();
    body.append("text", textarea.value);
    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "X-CSRFToken": token,
      },
      body: body.toString(),
      credentials: "same-origin",
      signal: wrapper._previewAbort.signal,
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Preview request failed");
        }
        return response.json();
      })
      .then(function (data) {
        output.innerHTML = data.html || "";
      })
      .catch(function (err) {
        if (err && err.name === "AbortError") {
          return;
        }
      });
  }

  function bindWidget(wrapper) {
    var textarea = wrapper.querySelector("textarea");
    var timer = null;
    if (!textarea) {
      return;
    }
    textarea.addEventListener("input", function () {
      if (timer) {
        clearTimeout(timer);
      }
      timer = setTimeout(function () {
        renderPreview(wrapper);
      }, DEBOUNCE_MS);
    });
    renderPreview(wrapper);
  }

  function init() {
    var widgets = document.querySelectorAll(".markdown-preview-widget");
    var i;
    for (i = 0; i < widgets.length; i += 1) {
      bindWidget(widgets[i]);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
