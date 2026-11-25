from django.urls import path
from . import views

app_name = "attendance"

urlpatterns = [
    path("event/<uuid:event_id>/", views.mark_attendance_view, name="mark"),
]