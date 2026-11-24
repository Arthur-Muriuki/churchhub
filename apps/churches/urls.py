from django.urls import path
from . import views

app_name = "churches"

urlpatterns = [
    path("settings/", views.church_settings_view, name="settings"),
]