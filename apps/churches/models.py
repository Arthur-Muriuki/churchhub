import uuid
from django.core.validators import RegexValidator
from django.db import models


class ChurchProfile(models.Model):
    """
    Single-church configuration model enabling any church (e.g., RGC Subukia)
    to customize branding, contact details, certificate headers, and privacy policies
    without modifying source code.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, default="ChurchHub Local Assembly")
    short_name = models.CharField(max_length=50, default="ChurchHub", help_text="Displayed in sidebar header")
    denomination = models.CharField(max_length=150, blank=True)
    motto = models.CharField(max_length=255, blank=True)
    hex_color_validator = RegexValidator(
    regex=r"^#[0-9A-Fa-f]{6}$",
    message="Enter a valid 6-digit hex color code (e.g., #0A2540).",
)
# Configurable UI Theme Colors (Defaults to SRS Navy Blue #0A2540)
    primary_color = models.CharField(
        max_length=7,
        default="#0A2540",
        validators=[hex_color_validator],
        help_text="Main navigation, sidebar, and primary buttons.",
    )
    secondary_color = models.CharField(
        max_length=7,
        default="#1E293B",
        validators=[hex_color_validator],
        help_text="Sidebar hover states and secondary headers.",
    )
    accent_color = models.CharField(
        max_length=7,
        default="#2563EB",
        validators=[hex_color_validator],
        help_text="Active links, badges, and highlights.",
    )
    # Branding & Certificate Assets
    logo = models.ImageField(upload_to="church_branding/", blank=True, null=True)
    official_stamp_or_signature = models.ImageField(
        upload_to="church_branding/",
        blank=True,
        null=True,
        help_text="Optional digital stamp/signature rendered on official PDF certificates.",
    )

    # Contact & Service Information
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    physical_address = models.CharField(max_length=255, blank=True)
    postal_address = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    service_schedule = models.TextField(
        blank=True,
        default="Sunday Main Service: 9:00 AM - 12:00 PM\nMidweek Fellowship: Wednesday 5:30 PM",
    )

    # Official Signatories & Document Configuration
    senior_pastor_name = models.CharField(max_length=150, blank=True)
    church_secretary_name = models.CharField(max_length=150, blank=True)
    certificate_footer_note = models.CharField(
        max_length=255,
        default="Official digital record verified by Church Administration.",
    )

    # Configurable Privacy & Workflow Toggles (Kenya Data Protection Act & Privacy Policy)
    enable_confidential_pastoral_notes = models.BooleanField(
        default=True,
        help_text="Enable encrypted pastoral counselling notes module per church privacy policy.",
    )
    require_registration_consent = models.BooleanField(
        default=True,
        help_text="Require explicit member data consent acknowledgment per Kenya Data Protection Act (2019).",
    )
    data_privacy_statement = models.TextField(
        default=(
            "Personal information collected by the church is processed strictly for pastoral care, "
            "membership administration, and ministry coordination in accordance with the Kenya Data Protection Act (2019)."
        )
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Church Profile & Settings"
        verbose_name_plural = "Church Profile & Settings"

    @classmethod
    def get_solo(cls):
        """
        Retrieves the active church configuration, creating a default record if none exists.
        """
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create()
        return obj

    def __str__(self):
        return self.name