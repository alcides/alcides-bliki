import string
from random import choice
import unittest

from django.template.defaultfilters import slugify
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite

from django_markup.templatetags.markup_tags import apply_markup
from wiki.admin import PageAdmin
from wiki.models import *
from wiki.widgets import AdminMarkdownPreviewWidget

class PageTestCase(unittest.TestCase):
  
  def randomTitle(self, size = 10):
    chars = string.digits + string.letters + " .-_+?!"
    return "".join([ choice(chars) for i in range(size)])
  
  def setUp(self):
    self.u =  User.objects.create_user("jsmith", "jsmith@example.com", "test123")
    self.l = Language.objects.create(name="Portuguese",code="pt-PT")
    self.t = self.randomTitle() 
    self.slug = slugify(self.t)
    self.c = Page.objects.create(
      title = self.t,
      slug = self.slug,
      author = self.u,
      lang = self.l,
      text = "whatever"
    )
    
  def tearDown(self):
    self.u.delete()
    self.l.delete()
    PageVersion.objects.filter( id=self.c.id ).delete()
    self.c.delete()

  def singleTestVersioning(self):
    self.count_before = PageVersion.objects.filter(page__id=self.c.id).count()
    self.c.text = self.c.text + " one bit"
    self.c.save()
    self.count_after = PageVersion.objects.filter(page__id=self.c.id).count()
    self.assertEquals(self.count_before + 1, self.count_after)
    
  def testVersioning(self):
    for _ in range(5):
      self.singleTestVersioning()
    
  def testPageIsViewed(self):
    c = Client()
    response = c.get("/%s" % self.slug)
    self.failUnlessEqual(response.status_code, 301)
    response = c.get("/%s/" % self.slug)    
    self.failUnlessEqual(response.status_code, 200)    

class MarkdownMarkupTestCase(TestCase):

  def test_headings(self):
    rendered = str(apply_markup("# Hello World\n\n## Subtitle", "markdown"))
    self.assertIn("Hello World", rendered)
    self.assertIn("Subtitle", rendered)
    self.assertIn("<h1", rendered)
    self.assertIn("<h2", rendered)

  def test_links(self):
    rendered = str(apply_markup("See [example](https://example.com/) for more.", "markdown"))
    self.assertIn("example.com", rendered)
    self.assertIn("<a", rendered)

  def test_emphasis(self):
    rendered = str(apply_markup("This is **bold** and *italic*.", "markdown"))
    self.assertIn("<strong>", rendered)
    self.assertIn("bold", rendered)
    self.assertIn("<em>", rendered)
    self.assertIn("italic", rendered)

  def test_lists(self):
    rendered = str(apply_markup("* item one\n* item two", "markdown"))
    self.assertIn("<ul>", rendered)
    self.assertIn("item one", rendered)
    self.assertIn("item two", rendered)

  def test_code(self):
    inline = str(apply_markup("Use `print()` here.", "markdown"))
    self.assertIn("<code>", inline)
    self.assertIn("print()", inline)

    block = "```\ndef foo():\n    return 1\n```"
    rendered = str(apply_markup(block, "markdown"))
    self.assertIn("<pre>", rendered)
    self.assertIn("<code>", rendered)
    self.assertIn("def foo():", rendered)
    self.assertIn("return 1", rendered)

    lang = "```python\nprint(1)\n```"
    rendered_lang = str(apply_markup(lang, "markdown"))
    self.assertIn("<pre>", rendered_lang)
    self.assertIn("print(1)", rendered_lang)

  def test_images(self):
    rendered = str(apply_markup("![Alt text](https://example.com/pic.png)", "markdown"))
    self.assertIn("<img", rendered)
    self.assertIn("example.com/pic.png", rendered)
    self.assertIn("Alt text", rendered)

  def test_blockquotes(self):
    rendered = str(apply_markup("> A quoted thought.", "markdown"))
    self.assertIn("<blockquote", rendered)
    self.assertIn("A quoted thought.", rendered)

  def test_footnotes(self):
    md = (
      "A sentence[^1] with a footnote and another[^2].\n\n"
      "[^1]: The first definition.\n\n"
      "[^2]: Second note with [a link](https://example.com/)."
    )
    rendered = str(apply_markup(md, "markdown"))
    self.assertIn("<sup", rendered)
    self.assertIn('href="#fn:1"', rendered)
    self.assertIn('id="fn:1"', rendered)
    self.assertIn("The first definition.", rendered)
    self.assertIn('class="footnote"', rendered)
    self.assertIn("footnote-ref", rendered)
    self.assertNotIn("[1](#", rendered)
    self.assertIn("a link", rendered)

  def test_youtube_iframe_survives_render(self):
    md = (
      '<iframe width="560" height="315" '
      'src="https://www.youtube.com/embed/V4UWxlVvT1A" '
      'frameborder="0" allowfullscreen></iframe>'
    )
    rendered = str(apply_markup(md, "markdown"))
    self.assertIn("<iframe", rendered)
    self.assertIn("youtube.com/embed/V4UWxlVvT1A", rendered)
    self.assertIn("allowfullscreen", rendered.lower())

    protocol_relative = (
      '<iframe width="560" height="315" '
      'src="//www.youtube.com/embed/H08tGjXNHO4" '
      'frameborder="0" allowfullscreen></iframe>'
    )
    rendered_rel = str(apply_markup(protocol_relative, "markdown"))
    self.assertIn("<iframe", rendered_rel)
    self.assertIn("youtube.com/embed/H08tGjXNHO4", rendered_rel)

  def test_embed_only_page_is_not_empty(self):
    iframe_only = (
      '<iframe src="http://astore.amazon.com/alcidfonse-20" '
      'width="100%" height="4000" frameborder="0" scrolling="no"></iframe>'
    )
    rendered = str(apply_markup(iframe_only, "markdown"))
    self.assertTrue(rendered.strip())
    self.assertIn("<iframe", rendered)

    gist_only = '<script src="https://gist.github.com/1254484.js"> </script>'
    gist_rendered = str(apply_markup(gist_only, "markdown"))
    self.assertTrue(gist_rendered.strip())
    self.assertIn("<script", gist_rendered)
    self.assertIn("gist.github.com", gist_rendered)

  def test_flash_object_embed_survives(self):
    md = (
      '<object width="560" height="340">'
      '<param name="movie" value="http://www.youtube.com/v/b7j7b-iLPU4&hl=en&fs=1&">'
      "</param>"
      '<param name="allowFullScreen" value="true"></param>'
      '<param name="allowscriptaccess" value="always"></param>'
      '<embed src="http://www.youtube.com/v/b7j7b-iLPU4&hl=en&fs=1&" '
      'type="application/x-shockwave-flash" allowscriptaccess="always" '
      'allowfullscreen="true" width="560" height="340"></embed>'
      "</object>"
    )
    rendered = str(apply_markup(md, "markdown"))
    self.assertIn("<object", rendered)
    self.assertIn("<embed", rendered)
    self.assertIn("<param", rendered)
    self.assertIn("youtube.com/v/b7j7b-iLPU4", rendered)

  def test_javascript_iframe_src_is_stripped(self):
    md = '<iframe src="javascript:alert(1)" width="100" height="100"></iframe>'
    rendered = str(apply_markup(md, "markdown"))
    self.assertIn("<iframe", rendered)
    self.assertNotIn("javascript:", rendered.lower())

  def test_tables_stay_tables_with_images(self):
    md = (
      '<table><tr>'
      '<td><img src="https://example.com/a.jpg" alt=""></td>'
      '<td><img src="https://example.com/b.jpg" alt=""></td>'
      '</tr></table>'
    )
    rendered = str(apply_markup(md, "markdown"))
    self.assertIn("<table", rendered)
    self.assertIn("<td", rendered)
    self.assertIn("<img", rendered)
    self.assertIn("example.com/a.jpg", rendered)
    self.assertNotIn("| --- |", rendered)

  def test_nested_lists_keep_hierarchy(self):
    md = "* Security.\n    * Make storage encrypted.\n* Administrative tasks"
    rendered = str(apply_markup(md, "markdown"))
    self.assertIn("<ul>", rendered)
    self.assertRegex(rendered, r"<li>[\s\S]*<ul>")
    self.assertIn("Make storage encrypted", rendered)

  def test_span_caps_survives(self):
    md = 'This <span class="caps">OVA</span> is an acronym.'
    rendered = str(apply_markup(md, "markdown"))
    self.assertIn('class="caps"', rendered)
    self.assertIn("OVA", rendered)

  def test_numbered_paragraphs_are_not_ordered_lists(self):
    md = "1\\. First instruction stays a paragraph.\n\n2\\. Second too."
    rendered = str(apply_markup(md, "markdown"))
    self.assertIn("1.", rendered)
    self.assertNotIn("<ol>", rendered)


class MarkdownPageRenderTestCase(TestCase):

  def setUp(self):
    self.user = User.objects.create_user("markupuser", "markup@example.com", "test123")
    self.lang = Language.objects.create(name="English", code="en")
    self.client = Client()

  def _page(self, slug, text, pubdate=None):
    return Page.objects.create(
      title=slug,
      slug=slug,
      author=self.user,
      lang=self.lang,
      text=text,
      pubdate=pubdate,
    )

  def test_detail_renders_markdown_from_text(self):
    page = self._page("hello", text="# Markdown Heading")
    response = self.client.get("/%s/" % page.slug)
    self.assertEqual(response.status_code, 200)
    content = response.content.decode()
    self.assertIn("Markdown Heading", content)
    self.assertIn("<h1", content)
    self.assertIn(str(apply_markup(page.text, "markdown")).strip(), content)

  def test_markup_query_param_is_ignored(self):
    page = self._page("hello", text="# Markdown Heading")
    default = self.client.get("/%s/" % page.slug)
    ignored = self.client.get("/%s/" % page.slug, {"markup": "ignored"})
    markdown = self.client.get("/%s/" % page.slug, {"markup": "markdown"})
    self.assertEqual(default.status_code, 200)
    self.assertEqual(ignored.status_code, 200)
    self.assertEqual(markdown.status_code, 200)
    self.assertEqual(default.content, ignored.content)
    self.assertEqual(default.content, markdown.content)
    content = ignored.content.decode()
    self.assertIn("Markdown Heading", content)
    self.assertIn("<h1", content)

  def test_list_always_renders_markdown(self):
    self._page(
      "listed",
      text="# Markdown Heading",
      pubdate=timezone.now(),
    )
    default = self.client.get("/")
    ignored = self.client.get("/", {"markup": "ignored"})
    self.assertEqual(default.status_code, 200)
    self.assertEqual(ignored.status_code, 200)
    self.assertIn("Markdown Heading", default.content.decode())
    self.assertIn("Markdown Heading", ignored.content.decode())
    self.assertEqual(default.content, ignored.content)

  def test_pagination_has_no_markup_query(self):
    now = timezone.now()
    for i in range(21):
      self._page(
        "page-%02d" % i,
        text="# Markdown %d" % i,
        pubdate=now,
      )
    default = self.client.get("/")
    ignored = self.client.get("/", {"markup": "ignored"})
    self.assertContains(default, 'href="?page=2"', status_code=200)
    self.assertNotContains(default, "markup=")
    self.assertContains(ignored, 'href="?page=2"', status_code=200)
    self.assertNotContains(ignored, "markup=")

  def test_page_renders_markdown_footnotes(self):
    md = "Hello[^1] world.\n\n[^1]: A converted note."
    page = self._page("fn-page", text=md)
    response = self.client.get("/%s/" % page.slug)
    self.assertEqual(response.status_code, 200)
    content = response.content.decode()
    self.assertIn("<sup", content)
    self.assertIn('href="#fn:1"', content)
    self.assertIn("A converted note.", content)
    self.assertIn('class="footnote"', content)
    self.assertNotIn("[1](#", content)

  def test_page_renders_iframe_embeds(self):
    md = (
      '<iframe width="560" height="315" '
      'src="https://www.youtube.com/embed/V4UWxlVvT1A" '
      'frameborder="0" allowfullscreen></iframe>'
    )
    page = self._page("embed-page", text=md)
    response = self.client.get("/%s/" % page.slug)
    self.assertEqual(response.status_code, 200)
    content = response.content.decode()
    self.assertIn("<iframe", content)
    self.assertIn("youtube.com/embed/V4UWxlVvT1A", content)


class AdminMarkdownPreviewTestCase(TestCase):

  def setUp(self):
    self.staff = User.objects.create_user(
      "previewstaff",
      "previewstaff@example.com",
      "test123",
      is_staff=True,
    )
    self.superuser = User.objects.create_superuser(
      "previewadmin",
      "previewadmin@example.com",
      "test123",
    )
    self.regular = User.objects.create_user(
      "previewuser",
      "previewuser@example.com",
      "test123",
    )
    self.url = reverse("admin:wiki_page_markdown_preview")
    self.sample_markdown = (
      "# Preview Heading\n\n"
      "A sentence with a footnote.[^1]\n\n"
      "```\n"
      "def hello():\n"
      "    return 42\n"
      "```\n\n"
      "[^1]: Footnote definition text.\n"
    )

  def _html(self, response):
    return response.json()["html"]

  def test_anonymous_is_rejected(self):
    client = Client()
    get_response = client.get(self.url)
    post_response = client.post(self.url, {"text": "# Hi"})
    self.assertIn(get_response.status_code, (302, 403))
    self.assertIn(post_response.status_code, (302, 403))

  def test_non_staff_is_rejected(self):
    client = Client()
    client.force_login(self.regular)
    get_response = client.get(self.url)
    post_response = client.post(self.url, {"text": "# Hi"})
    self.assertIn(get_response.status_code, (302, 403))
    self.assertIn(post_response.status_code, (302, 403))

  def test_staff_get_is_not_rendered_post(self):
    self.client.force_login(self.staff)
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, 405)
    self.assertEqual(response.json()["html"], "")

  def test_staff_post_renders_markdown_extras(self):
    self.client.force_login(self.staff)
    response = self.client.post(self.url, {"text": self.sample_markdown})
    self.assertEqual(response.status_code, 200)
    html = self._html(response)
    expected = str(apply_markup(self.sample_markdown, "markdown"))
    self.assertEqual(html, expected)
    self.assertIn("<h1", html)
    self.assertIn("Preview Heading", html)
    self.assertIn("<sup", html)
    self.assertIn("footnote", html)
    self.assertIn("Footnote definition text.", html)
    self.assertIn("<pre>", html)
    self.assertIn("<code>", html)
    self.assertIn("def hello():", html)
    self.assertIn("return 42", html)

  def test_preview_does_not_echo_unsanitized_javascript_src(self):
    self.client.force_login(self.staff)
    payload = '<iframe src="javascript:alert(1)"></iframe>'
    response = self.client.post(self.url, {"text": payload})
    self.assertEqual(response.status_code, 200)
    html = self._html(response)
    self.assertNotIn("javascript:", html.lower())
    self.assertNotEqual(html, payload)

  def test_csrf_enforced_for_staff_post(self):
    csrf_client = Client(enforce_csrf_checks=True)
    csrf_client.force_login(self.staff)
    bare = csrf_client.post(self.url, {"text": "# Hi"})
    self.assertEqual(bare.status_code, 403)

    csrf_client.get(reverse("admin:index"))
    token = csrf_client.cookies["csrftoken"].value
    ok = csrf_client.post(
      self.url,
      {"text": "# CSRF Heading"},
      HTTP_X_CSRFTOKEN=token,
    )
    self.assertEqual(ok.status_code, 200)
    self.assertIn("CSRF Heading", ok.json()["html"])
    self.assertIn("<h1", ok.json()["html"])

  def test_text_field_uses_preview_widget_only(self):
    model_admin = PageAdmin(Page, AdminSite())
    request = RequestFactory().get("/")
    request.user = self.staff
    text_field = Page._meta.get_field("text")
    title_field = Page._meta.get_field("title")
    text_formfield = model_admin.formfield_for_dbfield(text_field, request)
    title_formfield = model_admin.formfield_for_dbfield(title_field, request)
    self.assertIsInstance(text_formfield.widget, AdminMarkdownPreviewWidget)
    self.assertNotIsInstance(title_formfield.widget, AdminMarkdownPreviewWidget)

  def test_admin_change_form_includes_preview_widget(self):
    lang = Language.objects.create(name="English", code="en")
    page = Page.objects.create(
      title="Preview Page",
      slug="preview-page",
      author=self.superuser,
      lang=lang,
      text="# Existing body",
    )
    self.client.force_login(self.superuser)
    response = self.client.get(
      reverse("admin:wiki_page_change", args=[page.pk])
    )
    self.assertEqual(response.status_code, 200)
    content = response.content.decode()
    self.assertIn("markdown-preview-widget", content)
    self.assertIn("data-preview-url", content)
    self.assertIn(self.url, content)
    self.assertIn("wiki/admin/markdown_preview.js", content)
    self.assertIn("wiki/admin/markdown_preview.css", content)
    self.assertIn("Existing body", content)
