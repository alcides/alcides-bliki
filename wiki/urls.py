from django.conf.urls.defaults import *
from views import *
from feeds import English, Portuguese, All

feeds = {
    'en': English,
    'pt': Portuguese,
	'all': All,
}

urlpatterns = patterns('',
	(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
	(r'^(?P<slug>\S+)$', page_detail),
    (r'^$', index),
)
