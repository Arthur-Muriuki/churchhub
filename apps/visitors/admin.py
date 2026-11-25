from django.contrib import admin
from .models import Visitor, VisitorFollowUp


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone_number", "visit_date", "status", "assigned_to", "next_followup_date")
    list_filter = ("status", "visit_date")
    search_fields = ("full_name", "phone_number", "email")


@admin.register(VisitorFollowUp)
class VisitorFollowUpAdmin(admin.ModelAdmin):
    list_display = ("visitor", "contact_date", "channel", "next_action_date", "recorded_by")
    list_filter = ("channel", "contact_date")