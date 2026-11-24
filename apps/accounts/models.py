import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class Permission(models.Model):
    """
    Granular system actions that can be assigned to any configurable Role.
    """
    code = models.CharField(max_length=100, unique=True, help_text="e.g., pastoral.view_confidential")
    name = models.CharField(max_length=150)
    module = models.CharField(max_length=50, help_text="e.g., members, pastoral, baptism, events")
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["module", "code"]

    def __str__(self):
        return f"[{self.module}] {self.name} ({self.code})"


class Role(models.Model):
    """
    Configurable organizational roles tailored per church deployment.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name="roles")
    is_system_role = models.BooleanField(
        default=False,
        help_text="Protects core template roles from accidental deletion.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Custom User model supporting configurable RBAC and UUID primary keys.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    must_change_password = models.BooleanField(default=False)

    def has_role_perm(self, perm_code: str) -> bool:
        """
        Checks if the user is a superuser or if their assigned Role holds perm_code.
        """
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        if not self.role:
            return False
        return self.role.permissions.filter(code=perm_code).exists()

    def __str__(self):
        role_label = self.role.name if self.role else "No Role"
        return f"{self.get_full_name() or self.username} ({role_label})"


class AuditLog(models.Model):
    """
    Immutable audit trail tracking sensitive operations and unauthorized access attempts.
    """
    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete (Soft)"),
        ("VIEW_SENSITIVE", "View Sensitive Record"),
        ("EXPORT", "Export / Print Document"),
        ("UNAUTHORIZED", "Unauthorized Access Attempt"),
        ("LOGIN", "User Login"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_model = models.CharField(max_length=100)
    target_id = models.CharField(max_length=100, blank=True)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        actor = self.user.username if self.user else "Anonymous"
        return f"{self.timestamp:%Y-%m-%d %H:%M} | {actor} | {self.action_type} | {self.target_model}"