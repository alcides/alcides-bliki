from django.conf import settings
from django.urls import path, re_path, include, register_converter
from django.conf.urls.static import static
from django.contrib import admin

from django.views.generic.detail import DetailView

from .models import Page
from .feeds import English, Portuguese, All
from .views import HomePageView, TagPageListView


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
    path('', HomePageView.as_view()),
    path('tag/<slug:slug>/', TagPageListView.as_view(), name='tag_page_list'),
    re_path('^(?!(admin|media|static))(?P<slug>[\w/\-_]*)/$', DetailView.as_view(queryset=Page.objects.all()), name="page_detail"),
]