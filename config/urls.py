from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("church/", include("churches.urls")),
    path("members/", include("members.urls")),
    path("departments/", include("departments.urls")),
    path("ministries/", include("ministries.urls")),
    path("baptism/", include("baptism.urls")),
    path("", include("reports.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)