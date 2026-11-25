from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path("", views.event_list_view, name="list"),
    path("add/", views.event_create_view, name="create"),
    path("<uuid:pk>/edit/", views.event_update_view, name="update"),
]