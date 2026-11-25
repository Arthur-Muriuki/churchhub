from django.urls import path
from . import views

app_name = "departments"

urlpatterns = [
    path("", views.department_list_view, name="list"),
    path("add/", views.department_create_view, name="create"),
    path("<uuid:pk>/", views.department_detail_view, name="detail"),
    path("<uuid:pk>/edit/", views.department_update_view, name="update"),
]
