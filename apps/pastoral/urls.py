from django.urls import path
from . import views

app_name = "pastoral"

urlpatterns = [
    path("", views.pastoral_list_view, name="list"),
    path("add/", views.pastoral_create_view, name="create"),
    path("<uuid:pk>/edit/", views.pastoral_update_view, name="update"),
]