import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from members.models import Member, validate_not_future_date


class BaptismRecord(models.Model):
    """
    Records water baptism details, unique certificate reference codes,
    and official verification status for a member or candidate.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate_number = models.CharField(
        max_length=40,
        unique=True,
        editable=False,
        db_index=True,
    )
    member = models.OneToOneField(
        Member,
        on_delete=models.CASCADE,
        related_name="baptism_record",
    )
    baptism_date = models.DateField(validators=[validate_not_future_date])
    officiating_minister = models.CharField(max_length=150)
    location_or_venue = models.CharField(max_length=180, blank=True)
    witness_name = models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)

    is_verified = models.BooleanField(
        default=True,
        help_text="Marks whether this baptism record is officially verified for certificate issuance.",
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_baptisms",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-baptism_date", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            year_part = self.baptism_date.year if self.baptism_date else timezone.localdate().year
            self.certificate_number = f"BAP-{year_part}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

        # Keep Member record synchronized with verified baptism status
        if self.is_verified and self.member:
            updates = []
            if not self.member.is_baptized:
                self.member.is_baptized = True
                updates.append("is_baptized")
            if self.member.baptism_date != self.baptism_date:
                self.member.baptism_date = self.baptism_date
                updates.append("baptism_date")
            if updates:
                updates.append("updated_at")
                self.member.save(update_fields=updates)

    def __str__(self):
        return f"{self.certificate_number} - {self.member.full_name}"