from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import AuditLog, Permission, Role, User


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("module", "code", "name")
    list_filter = ("module",)
    search_fields = ("code", "name")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_system_role", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("permissions",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("ChurchHub Role & Profile", {"fields": ("role", "phone_number", "must_change_password")}),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action_type", "target_model", "target_id", "ip_address")
    list_filter = ("action_type", "target_model", "timestamp")
    search_fields = ("user__username", "target_model", "details", "ip_address")
    readonly_fields = ("id", "user", "action_type", "target_model", "target_id", "details", "ip_address", "timestamp")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False