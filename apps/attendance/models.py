import uuid
from django.conf import settings
from django.db import models
from events.models import Event
from members.models import Member


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
        ("EXCUSED", "Excused / Apology"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendance_records")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="attendance_records")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="PRESENT")
    notes = models.CharField(max_length=255, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    recorded_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("event", "member")
        ordering = ["member__last_name", "member__first_name"]

    def __str__(self):
        return f"{self.member.full_name} - {self.event.title} ({self.get_status_display()})"