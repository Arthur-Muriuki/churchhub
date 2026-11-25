import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from departments.models import Department
from members.models import Member


class Ministry(models.Model):
    """
    Specialized sub-group or ministry operating independently or under a parent Department.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ministries",
    )
    description = models.TextField(blank=True)
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_ministries",
    )
    members = models.ManyToManyField(Member, related_name="ministries", blank=True)
    meeting_schedule = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Ministries"

    def __str__(self):
        return self.name


class MinistryActivity(models.Model):
    """
    Logs ministry meetings, outreach sessions, rehearsals, and departmental activities.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE, related_name="activities")
    title = models.CharField(max_length=150)
    activity_date = models.DateField(default=timezone.localdate)
    location = models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)
    attendance_count = models.PositiveIntegerField(default=0)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-activity_date", "-created_at"]
        verbose_name_plural = "Ministry Activities"

    def __str__(self):
        return f"{self.title} ({self.ministry.name} - {self.activity_date})"