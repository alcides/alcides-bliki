/* Point amazon.com shopping links at amazon.es for visitors in Spain or
 * Portugal, so they land on the marketplace they can actually order from
 * (and the Spanish Associates tracking ID gets credited).
 *
 * The server renders amazon.com links with the US tag (see
 * wiki/markdown_filter.py); location is only known client-side, and the
 * IANA timezone is a good proxy for being physically in Iberia without
 * needing GeoIP or per-request HTML.
 */
(function () {
  "use strict";

  var AMAZON_COM_HOSTS = ["amazon.com", "www.amazon.com", "smile.amazon.com"];
  var SPANISH_HOST = "www.amazon.es";
  var SPANISH_TAG = "alcidesfonsec-21";

  var IBERIAN_TIMEZONES = [
    // Spain
    "Europe/Madrid",
    "Africa/Ceuta",
    "Atlantic/Canary",
    // Portugal
    "Europe/Lisbon",
    "Atlantic/Madeira",
    "Atlantic/Azores",
  ];

  function isIberianTimeZone(timeZone) {
    return IBERIAN_TIMEZONES.indexOf(timeZone) !== -1;
  }

  function currentTimeZone() {
    try {
      return Intl.DateTimeFormat().resolvedOptions().timeZone || "";
    } catch (e) {
      return "";
    }
  }

  /* Returns the amazon.es version of an amazon.com shopping URL, or null
   * if the URL should be left alone. Path, query and fragment are kept;
   * the tracking tag is switched to the Spanish one. */
  function localizeUrl(href) {
    var url;
    try {
      url = new URL(href);
    } catch (e) {
      return null;
    }
    if (url.protocol !== "http:" && url.protocol !== "https:") {
      return null;
    }
    if (AMAZON_COM_HOSTS.indexOf(url.hostname.toLowerCase()) === -1) {
      return null;
    }
    url.hostname = SPANISH_HOST;
    url.searchParams.set("tag", SPANISH_TAG);
    return url.toString();
  }

  function localizeLinks(doc) {
    var anchors = doc.querySelectorAll("a[href]");
    for (var i = 0; i < anchors.length; i++) {
      var localized = localizeUrl(anchors[i].href);
      if (localized) {
        anchors[i].href = localized;
      }
    }
  }

  function run() {
    if (isIberianTimeZone(currentTimeZone())) {
      localizeLinks(document);
    }
  }

  var root = typeof window !== "undefined" ? window : globalThis;
  root.AmazonLocale = {
    localizeUrl: localizeUrl,
    isIberianTimeZone: isIberianTimeZone,
  };

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", run);
    } else {
      run();
    }
  }
})();
