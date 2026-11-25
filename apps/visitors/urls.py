from django.urls import path
from . import views

app_name = "visitors"

urlpatterns = [
    path("", views.visitor_list_view, name="list"),
    path("add/", views.visitor_create_view, name="create"),
    path("<uuid:pk>/", views.visitor_detail_view, name="detail"),
    path("<uuid:pk>/edit/", views.visitor_update_view, name="update"),
]