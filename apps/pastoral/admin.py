from django.contrib import admin
from .models import PastoralCareLog


@admin.register(PastoralCareLog)
class PastoralCareLogAdmin(admin.ModelAdmin):
    list_display = ("member", "category", "status", "session_date", "follow_up_date", "pastor")
    list_filter = ("category", "status", "session_date")
    search_fields = ("member__first_name", "member__last_name", "member__member_number")
    readonly_fields = ("encrypted_notes",)