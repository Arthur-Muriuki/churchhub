from django.urls import path
from . import views

app_name = "announcements"

urlpatterns = [
    path("", views.announcement_list_view, name="list"),
    path("add/", views.announcement_create_view, name="create"),
    path("<uuid:pk>/edit/", views.announcement_update_view, name="update"),
    path("<uuid:pk>/read/", views.announcement_mark_read_view, name="mark_read"),
]