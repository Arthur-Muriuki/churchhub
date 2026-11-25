import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from events.models import Event
from members.models import Member


class Visitor(models.Model):
    STATUS_CHOICES = [
        ("NEW", "New Visitor"),
        ("CONTACTED", "Contacted"),
        ("FOLLOW_UP_SCHEDULED", "Follow-Up Scheduled"),
        ("INTEGRATED", "Integrated / Joined"),
        ("CLOSED", "Closed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=140, db_index=True)
    phone_number = models.CharField(max_length=25, blank=True, db_index=True)
    email = models.EmailField(blank=True)
    residential_area = models.CharField(max_length=150, blank=True)
    visit_date = models.DateField(default=timezone.localdate, db_index=True)
    visited_event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visitors",
    )
    how_heard = models.CharField(max_length=150, blank=True, help_text="e.g., Invited by member, Poster, Social media")
    prayer_or_notes = models.TextField(blank=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default="NEW", db_index=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_visitors",
    )
    next_followup_date = models.DateField(null=True, blank=True)
    converted_member = models.OneToOneField(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visitor_origin",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_visitors",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-visit_date", "-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.visit_date})"


class VisitorFollowUp(models.Model):
    CHANNEL_CHOICES = [
        ("PHONE_CALL", "Phone Call"),
        ("HOME_VISIT", "Home / Office Visit"),
        ("CHURCH_MEETUP", "In-Person at Church"),
        ("SMS_WHATSAPP", "SMS / WhatsApp"),
        ("EMAIL", "Email"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name="followups")
    contact_date = models.DateField(default=timezone.localdate)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default="PHONE_CALL")
    summary = models.TextField()
    next_action_date = models.DateField(null=True, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-contact_date", "-created_at"]

    def __str__(self):
        return f"Follow-up on {self.visitor.full_name} ({self.contact_date})"