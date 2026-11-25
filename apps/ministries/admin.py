from django.contrib import admin
from .models import Ministry, MinistryActivity


@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "leader", "meeting_schedule", "is_active")
    list_filter = ("department", "is_active")
    search_fields = ("name",)


@admin.register(MinistryActivity)
class MinistryActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "ministry", "activity_date", "attendance_count", "recorded_by")
    list_filter = ("ministry", "activity_date")