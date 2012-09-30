from django.conf.urls.defaults import *
from models import Page
from feeds import English, Portuguese, All

urlpatterns = patterns('',
	(r'^feeds/all/$', All),
	(r'^feeds/pt/$', Portuguese),
	(r'^feeds/en/$', English),
	(r'^(?P<slug>\S+)/$', 'django.views.generic.list_detail.object_detail',{ 'queryset': Page.objects.all() }),
    (r'^$', 'django.views.generic.list_detail.object_list', {'queryset': Page.objects.filter(pubdate__isnull=False).order_by('-pubdate'), 'paginate_by': 20 }),
)
