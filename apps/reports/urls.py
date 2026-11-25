from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("reports/", views.report_center_view, name="center"),
    path("reports/export/csv/", views.export_report_csv_view, name="export_csv"),
]