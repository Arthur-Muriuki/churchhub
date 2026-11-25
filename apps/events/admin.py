from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "event_date", "location", "additional_headcount", "is_completed")
    list_filter = ("event_type", "event_date", "is_completed")
    search_fields = ("title", "location")