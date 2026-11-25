from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "member_number",
        "full_name",
        "phone_number",
        "membership_status",
        "is_baptized",
        "consent_given",
        "is_active",
    )
    list_filter = ("membership_status", "is_baptized", "consent_given", "is_active", "gender")
    search_fields = ("member_number", "first_name", "last_name", "email", "phone_number")