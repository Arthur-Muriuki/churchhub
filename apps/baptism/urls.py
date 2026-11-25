from django.urls import path
from . import views

app_name = "baptism"

urlpatterns = [
    path("", views.baptism_list_view, name="list"),
    path("add/", views.baptism_create_view, name="create"),
    path("<uuid:pk>/edit/", views.baptism_update_view, name="update"),
    path("<uuid:pk>/certificate.pdf", views.baptism_certificate_pdf_view, name="certificate_pdf"),
]