from django.contrib import admin
from .models import Announcement, AnnouncementReadReceipt


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "priority", "publish_date", "expires_on", "is_pinned", "is_published")
    list_filter = ("category", "priority", "is_pinned", "is_published", "publish_date")
    search_fields = ("title", "body")


@admin.register(AnnouncementReadReceipt)
class AnnouncementReadReceiptAdmin(admin.ModelAdmin):
    list_display = ("announcement", "user", "read_at")
    list_filter = ("read_at",)