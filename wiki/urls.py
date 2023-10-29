from django.conf import settings
from django.urls import path, re_path, include, register_converter
from django.conf.urls.static import static
from django.contrib import admin

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Page
from .feeds import English, Portuguese, All


class SlugConverter:
    regex = '[\w/]+'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)

register_converter(SlugConverter, 'myslug')



urlpatterns = [
    path('feeds/all/', All()),
	path('feeds/pt/', Portuguese()),
	path('feeds/en/', English()),
    path('', ListView.as_view(queryset= Page.objects.filter(pubdate__isnull=False).order_by('-pubdate'), paginate_by=20 )),
    re_path('^(?!(admin|media|static))(?P<slug>[\w/\-_]*)/$', DetailView.as_view(queryset=Page.objects.all()), name="page_detail"),
]