from django.urls import path
from . import views

app_name = "members"

urlpatterns = [
    path("", views.member_list_view, name="list"),
    path("add/", views.member_create_view, name="create"),
    path("<uuid:pk>/", views.member_detail_view, name="detail"),
    path("<uuid:pk>/edit/", views.member_update_view, name="update"),
    path("<uuid:pk>/archive/", views.member_soft_delete_view, name="delete"),
]