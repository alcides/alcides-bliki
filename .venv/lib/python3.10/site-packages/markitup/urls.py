from __future__ import unicode_literals

from django.urls import re_path

from markitup.views import apply_filter

urlpatterns = [
    re_path(r'preview/$', apply_filter, name='markitup_preview'),
]
