import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from members.models import Member
from .encryption import decrypt_text, encrypt_text


class PastoralCareLog(models.Model):
    """
    Stores restricted pastoral/counselling sessions with application-layer
    encryption on confidential notes and follow-up tracking.
    """
    STATUS_CHOICES = [
        ("OPEN", "Open / Active"),
        ("IN_PROGRESS", "In Progress"),
        ("FOLLOW_UP", "Follow-Up Scheduled"),
        ("RESOLVED", "Resolved / Closed"),
    ]

    CATEGORY_CHOICES = [
        ("COUNSELLING", "Counselling Session"),
        ("PASTORAL_VISIT", "Pastoral / Hospital Visit"),
        ("PRAYER_CARE", "Prayer & Spiritual Care"),
        ("FAMILY_MARRIAGE", "Family / Marriage Support"),
        ("BEREAVEMENT", "Bereavement Care"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="pastoral_logs",
    )
    category = models.CharField(max_length=25, choices=CATEGORY_CHOICES, default="COUNSELLING")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN", db_index=True)
    session_date = models.DateField(default=timezone.localdate, db_index=True)
    follow_up_date = models.DateField(null=True, blank=True)

    # Encrypted at application layer before saving to database
    encrypted_notes = models.TextField(editable=False)

    pastor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pastoral_care_logs",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-session_date", "-created_at"]

    def set_confidential_notes(self, plain_text: str):
        self.encrypted_notes = encrypt_text(plain_text or "")

    def get_confidential_notes(self) -> str:
        return decrypt_text(self.encrypted_notes)

    def __str__(self):
        return f"{self.get_category_display()} - {self.member.full_name} ({self.session_date})"