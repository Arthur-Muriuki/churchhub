import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from departments.models import Department
from ministries.models import Ministry


class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ("SUNDAY_SERVICE", "Sunday Service"),
        ("MIDWEEK_SERVICE", "Midweek / Prayer Service"),
        ("MINISTRY_MEETING", "Department / Ministry Meeting"),
        ("CONFERENCE_SEMINAR", "Conference / Seminar"),
        ("OUTREACH_FELLOWSHIP", "Outreach / Fellowship"),
        ("OTHER", "Other Church Event"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=160)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES, default="SUNDAY_SERVICE")
    event_date = models.DateField(default=timezone.localdate, db_index=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=180, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    ministry = models.ForeignKey(
        Ministry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    description = models.TextField(blank=True)
    additional_headcount = models.PositiveIntegerField(
        default=0,
        help_text="Optional headcount for visitors, children, or walk-ins not checked in individually.",
    )
    is_completed = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-event_date", "-created_at"]

    @property
    def present_members_count(self):
        return self.attendance_records.filter(status="PRESENT").count()

    @property
    def total_attendance(self):
        return self.present_members_count + self.additional_headcount

    def __str__(self):
        return f"{self.title} ({self.event_date})"