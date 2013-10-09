from django.conf.urls.defaults import *
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from models import Page
from feeds import English, Portuguese, All


urlpatterns = patterns('',
	(r'^feeds/all/$', All()),
	(r'^feeds/pt/$', Portuguese()),
	(r'^feeds/en/$', English()),
	(r'^(?P<slug>\S+)/$', DetailView.as_view(queryset=Page.objects.all())),
    (r'^$', ListView.as_view(queryset= Page.objects.filter(pubdate__isnull=False).order_by('-pubdate'), paginate_by=20 )),
)
