from django.conf import settings
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.contrib import admin

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView




from .models import Page
from .feeds import English, Portuguese, All

urlpatterns = [
    path('feeds/all/', All()),
	path('feeds/pt/', Portuguese()),
	path('feeds/en/', English()),
    path('<slug:slug>/', DetailView.as_view(queryset=Page.objects.all())),
    path('', ListView.as_view(queryset= Page.objects.filter(pubdate__isnull=False).order_by('-pubdate'), paginate_by=20 )),
]