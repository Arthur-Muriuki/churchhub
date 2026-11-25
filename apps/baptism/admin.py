from django.contrib import admin
from .models import BaptismRecord


@admin.register(BaptismRecord)
class BaptismRecordAdmin(admin.ModelAdmin):
    list_display = ("certificate_number", "member", "baptism_date", "officiating_minister", "is_verified")
    list_filter = ("is_verified", "baptism_date")
    search_fields = ("certificate_number", "member__first_name", "member__last_name", "officiating_minister")
    readonly_fields = ("certificate_number",)