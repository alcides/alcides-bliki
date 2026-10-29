from html.parser import HTMLParser

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from wiki.metadata import preview_description, preview_image
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


class PreviewImageTests(SimpleTestCase):
    def test_uses_first_markdown_image(self):
        self.assertEqual(
            preview_image(
                '![First diagram](/media/images/first.png)\n\n'
                '![Second diagram](https://example.com/second.png)',
                'https://example.com/blog/post/',
            ),
            {'url': 'https://example.com/media/images/first.png', 'alt': 'First diagram'},
        )

    def test_resolves_html_image_sources(self):
        for source, expected in [
            ('chart.png', 'https://example.com/blog/post/chart.png'),
            ('../chart.png', 'https://example.com/blog/chart.png'),
            ('//cdn.example.com/chart.png', 'https://cdn.example.com/chart.png'),
            ('https://cdn.example.com/chart.png', 'https://cdn.example.com/chart.png'),
            ('/media/a b.png?x=1&amp;y=2', 'https://example.com/media/a%20b.png?x=1&y=2'),
        ]:
            with self.subTest(source=source):
                self.assertEqual(
                    preview_image(f'<img src="{source}" alt="A &amp; B">', 'https://example.com/blog/post/'),
                    {'url': expected, 'alt': 'A & B'},
                )

    def test_skips_empty_and_non_http_sources(self):
        self.assertEqual(
            preview_image(
                '<img><img src=""><img src="javascript:alert(1)">'
                '<img src="data:image/png;base64,abc"><img src="mailto:test@example.com">'
                '<img src="/media/usable.png">',
                'https://example.com/blog/post/',
            ),
            {'url': 'https://example.com/media/usable.png', 'alt': ''},
        )

    def test_returns_none_when_post_has_no_images(self):
        self.assertIsNone(preview_image('A **text-only** post.', 'https://example.com/post/'))


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
            'twitter:card': 'summary_large_image',
            'twitter:title': self.page.title,
            'twitter:description': description,
            'og:image': 'https://testserver/media/images/alcides_fonseca.jpg',
            'twitter:image': 'https://testserver/media/images/alcides_fonseca.jpg',
            'og:image:alt': 'Alcides Fonseca',
            'twitter:image:alt': 'Alcides Fonseca',
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
        response = self.client.get('/', secure=True)
        self.assertEqual(response.status_code, 200)
        head = _HeadMetadata(response.content.decode())
        self.assertNotIn('og:type', head.meta)
        self.assertEqual(head.meta['twitter:card'], ['summary_large_image'])
        self.assertEqual(head.meta['og:image'], ['https://testserver/media/images/alcides_fonseca.jpg'])
        self.assertEqual(head.meta['twitter:image'], head.meta['og:image'])
        self.assertEqual(head.canonical, [])

    def test_post_image_replaces_fallback_and_escapes_attributes(self):
        self.page.text = '![A "diagram" & example](/media/images/diagram.png?x=1&y=2)'
        self.page.save()
        response = self.client.get(self.page.get_absolute_url(), secure=True)
        head = _HeadMetadata(response.content.decode())
        self.assertEqual(head.meta['og:image'], ['https://testserver/media/images/diagram.png?x=1&y=2'])
        self.assertEqual(head.meta['twitter:image'], head.meta['og:image'])
        self.assertEqual(head.meta['og:image:alt'], ['A "diagram" & example'])
        self.assertContains(response, 'content="A &quot;diagram&quot; &amp; example"')
        self.assertNotIn('https://testserver/media/images/alcides_fonseca.jpg', head.meta['og:image'])
