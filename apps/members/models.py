import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def validate_not_future_date(value):
    if value and value > timezone.localdate():
        raise ValidationError("Date cannot be in the future.")


class Member(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
    ]

    MARITAL_STATUS_CHOICES = [
        ("SINGLE", "Single"),
        ("MARRIED", "Married"),
        ("WIDOWED", "Widowed"),
        ("DIVORCED", "Divorced"),
        ("UNSPECIFIED", "Prefer not to say"),
    ]

    MEMBERSHIP_STATUS_CHOICES = [
        ("ACTIVE", "Active Member"),
        ("TRANSFERRED", "Transferred Out"),
        ("INACTIVE", "Inactive / Dormant"),
        ("DECEASED", "Deceased"),
    ]

    member_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        help_text="Optional internal member ID or ledger reference (auto-generated if blank).",
    )
    user_account = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="member_profile",
    )

    # Core Demographics
    first_name = models.CharField(max_length=50, db_index=True)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, db_index=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        validators=[validate_not_future_date],
    )
    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        default="UNSPECIFIED",
    )

    # Contact & Household Information
    phone_number = models.CharField(max_length=25, blank=True, db_index=True)
    email = models.EmailField(blank=True, db_index=True)
    residential_area = models.CharField(max_length=150, blank=True)
    postal_address = models.CharField(max_length=120, blank=True)
    emergency_contact_name = models.CharField(max_length=120, blank=True)
    emergency_contact_phone = models.CharField(max_length=25, blank=True)

    # Church Membership & Status Lifecycle
    membership_status = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_STATUS_CHOICES,
        default="ACTIVE",
        db_index=True,
    )
    date_joined = models.DateField(
        default=timezone.localdate,
        validators=[validate_not_future_date],
    )
    transfer_notes = models.TextField(
        blank=True,
        help_text="Details for member transfers, status changes, or prior congregation notes.",
    )
    is_baptized = models.BooleanField(default=False)
    baptism_date = models.DateField(
        null=True,
        blank=True,
        validators=[validate_not_future_date],
    )

    # Data Protection Act Consent & Soft Delete
    consent_given = models.BooleanField(
        default=False,
        help_text="Member gave explicit consent for processing personal data.",
    )
    consent_timestamp = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Soft-delete flag: False indicates deactivated/archived record.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["membership_status", "is_active"]),
        ]

    def save(self, *args, **kwargs):
        if not self.member_number:
            self.member_number = f"MBR-{uuid.uuid4().hex[:8].upper()}"
        if self.consent_given and not self.consent_timestamp:
            self.consent_timestamp = timezone.now()
        elif not self.consent_given:
            self.consent_timestamp = None
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(part.strip() for part in parts if part and part.strip())

    def __str__(self):
        return f"{self.full_name} ({self.member_number})"