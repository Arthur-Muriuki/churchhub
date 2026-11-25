import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from departments.models import Department
from ministries.models import Ministry


class Announcement(models.Model):
    CATEGORY_CHOICES = [
        ("GENERAL", "General Announcement"),
        ("EVENT", "Event Notification"),
        ("ADMIN", "Administrative Notice"),
        ("MINISTRY", "Ministry Update"),
    ]

    PRIORITY_CHOICES = [
        ("NORMAL", "Normal"),
        ("IMPORTANT", "Important"),
        ("URGENT", "Urgent"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=180, db_index=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="GENERAL", db_index=True)
    priority = models.CharField(max_length=15, choices=PRIORITY_CHOICES, default="NORMAL", db_index=True)
    body = models.TextField()

    # Optional audience scoping (leave blank for church-wide notices)
    target_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="announcements",
    )
    target_ministry = models.ForeignKey(
        Ministry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="announcements",
    )

    is_pinned = models.BooleanField(default=False, db_index=True)
    is_published = models.BooleanField(default=True, db_index=True)
    publish_date = models.DateField(default=timezone.localdate, db_index=True)
    expires_on = models.DateField(null=True, blank=True)

    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="AnnouncementReadReceipt",
        related_name="read_announcements",
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_announcements",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_pinned", "-publish_date", "-created_at"]

    @property
    def is_expired(self):
        return bool(self.expires_on and self.expires_on < timezone.localdate())

    def __str__(self):
        return f"{self.title} ({self.publish_date})"


class AnnouncementReadReceipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name="read_receipts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="announcement_receipts")
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("announcement", "user")
        ordering = ["-read_at"]

    def __str__(self):
        return f"{self.user.username} read {self.announcement.title}"