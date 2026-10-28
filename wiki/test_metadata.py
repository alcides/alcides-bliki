from html.parser import HTMLParser

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from wiki.metadata import preview_description
from wiki.models import Language, Page


class PreviewDescriptionTests(SimpleTestCase):
    def test_renders_markdown_and_preserves_word_boundaries(self):
        self.assertEqual(
            preview_description(
                '# Heading\n\nA **bold** [link](https://example.com/).\n\n'
                '<p>Fish &amp; chips<br>Next line.</p>'
            ),
            'Heading A bold link. Fish & chips Next line.',
        )

    def test_excludes_script_and_style_contents(self):
        self.assertEqual(
            preview_description(
                '<script>secret();</script><style>body { color: red; }</style>'
                '<p>Visible text.</p>'
            ),
            'Visible text.',
        )

    def test_limits_description_to_160_characters(self):
        description = preview_description('A long description. ' * 30)
        self.assertEqual(len(description), 160)
        self.assertTrue(description.endswith('…'))

    def test_empty_content(self):
        self.assertEqual(preview_description(''), '')


class _HeadMetadata(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.in_head = False
        self.in_title = False
        self.meta = {}
        self.canonical = []
        self.title = ''
        self.feed_count = 0
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'head':
            self.in_head = True
        if not self.in_head:
            return
        attrs = dict(attrs)
        if tag == 'title':
            self.in_title = True
        if tag == 'meta':
            key = attrs.get('property', attrs.get('name'))
            self.meta.setdefault(key, []).append(attrs.get('content'))
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical.append(attrs['href'])
        if tag == 'link' and attrs.get('type') == 'application/rss+xml':
            self.feed_count += 1

    def handle_endtag(self, tag):
        if tag == 'head':
            self.in_head = False
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


class PageMetadataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = User.objects.create_user('preview-author')
        language = Language.objects.create(name='English', code='en')
        cls.page = Page.objects.create(
            title='20 years of Django',
            slug='blog/20-years-of-django',
            text='A **technical** blog about [Django](https://www.djangoproject.com/).',
            author=author,
            lang=language,
        )

    def test_preview_tags_are_in_the_head_with_a_clean_absolute_url(self):
        response = self.client.get(
            self.page.get_absolute_url(), {'utm_source': 'rss'}, secure=True,
        )
        self.assertEqual(response.status_code, 200)
        head = _HeadMetadata(response.content.decode())
        url = 'https://testserver/blog/20-years-of-django/'
        description = 'A technical blog about Django.'
        self.assertEqual(head.title, '20 years of Django by Alcides Fonseca')
        self.assertEqual(head.canonical, [url])
        for key, value in {
            'description': description,
            'og:title': self.page.title,
            'og:description': description,
            'og:url': url,
            'og:type': 'article',
            'og:site_name': 'Alcides Fonseca',
            'twitter:card': 'summary',
            'twitter:title': self.page.title,
            'twitter:description': description,
        }.items():
            self.assertEqual(head.meta[key], [value])
        self.assertEqual(head.feed_count, 2)

    def test_attribute_values_are_escaped(self):
        self.page.title = '<b>Quotes</b> " & more'
        self.page.text = '<p>A "quote" &amp; &lt;tag&gt;.</p>'
        self.page.save()
        response = self.client.get(self.page.get_absolute_url())
        head = _HeadMetadata(response.content.decode())
        self.assertEqual(head.meta['og:title'], ['Quotes " & more'])
        self.assertEqual(head.meta['description'], ['A "quote" & <tag>.'])
        self.assertContains(response, 'content="Quotes &quot; &amp; more"')
        self.assertContains(response, 'content="A &quot;quote&quot; &amp; &lt;tag&gt;."')

    def test_index_does_not_get_article_metadata(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        head = _HeadMetadata(response.content.decode())
        self.assertNotIn('og:type', head.meta)
        self.assertNotIn('twitter:card', head.meta)
        self.assertEqual(head.canonical, [])
