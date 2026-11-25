import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from members.models import Member


class Department(models.Model):
    """
    Configurable organizational department (e.g., Worship, Youth, Ushering, Media, Missions).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True)
    description = models.TextField(blank=True)
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_departments",
    )
    members = models.ManyToManyField(
        Member,
        through="DepartmentMembership",
        related_name="departments",
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"DEPT-{uuid.uuid4().hex[:5].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"


class DepartmentMembership(models.Model):
    """
    Tracks a member's participation and role inside a department.
    """
    ROLE_CHOICES = [
        ("MEMBER", "Member"),
        ("ASSISTANT_LEADER", "Assistant Leader"),
        ("COORDINATOR", "Coordinator"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="memberships")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="department_memberships")
    role_title = models.CharField(max_length=30, choices=ROLE_CHOICES, default="MEMBER")
    date_joined = models.DateField(default=timezone.localdate)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("department", "member")
        ordering = ["member__last_name", "member__first_name"]

    def __str__(self):
        return f"{self.member.full_name} in {self.department.name}"