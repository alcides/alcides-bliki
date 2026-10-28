import datetime
from django.utils import timezone
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from django.utils.html import strip_tags

from .metadata import preview_description
from .models import Page, Tag


def _published_pages():
    now = timezone.now()
    return Page.objects.filter(
        pubdate__isnull=False
    ).exclude(
        pubdate__gt=now
    ).order_by('-pubdate')


class HomePageView(ListView):
    model = Page
    template_name = 'wiki/page_list.html'
    paginate_by = 20
    context_object_name = 'object_list'

    def get_queryset(self):
        return _published_pages()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context['top_tags'] = Tag.objects.filter(
            pages__pubdate__isnull=False,
            pages__pubdate__lte=now,
        ).annotate(
            page_count=Count('pages', distinct=True),
        ).order_by('-page_count')[:10]
        return context


class TagPageListView(ListView):
    model = Page
    template_name = 'wiki/page_list.html'
    paginate_by = 20
    context_object_name = 'object_list'

    def get_queryset(self):
        tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return _published_pages().filter(tags=tag)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return context


class PageDetailView(DetailView):
	queryset = Page.objects.all().prefetch_related('tags')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['preview_title'] = ' '.join(strip_tags(self.object.title).split())
		context['preview_description'] = preview_description(self.object.text)
		context['canonical_url'] = self.request.build_absolute_uri(self.object.get_absolute_url())
		page_url = f'/{self.object.slug}/'

		if '/blog' in page_url and self.object.tags.exists():
			context['suggested_posts'] = (
				_published_pages()
				.filter(tags__in=self.object.tags.all())
				.exclude(pk=self.object.pk)
				.distinct()[:5]
			)

		return context
