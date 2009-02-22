from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
	
	(r'', include('wiki.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^public/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )