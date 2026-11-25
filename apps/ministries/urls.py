from django.urls import path
from . import views

app_name = "ministries"

urlpatterns = [
    path("", views.ministry_list_view, name="list"),
    path("add/", views.ministry_create_view, name="create"),
    path("<uuid:pk>/edit/", views.ministry_update_view, name="update"),
    path("activities/add/", views.activity_create_view, name="activity_create"),
]