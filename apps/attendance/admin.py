from django.contrib import admin
from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("event", "member", "status", "recorded_by", "recorded_at")
    list_filter = ("status", "event__event_date")
    search_fields = ("member__first_name", "member__last_name", "event__title")