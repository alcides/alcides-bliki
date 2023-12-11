from django.conf import settings
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r'', include('wiki.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
