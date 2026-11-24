from .models import AuditLog


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_audit(request, action_type: str, target_model: str, target_id: str = "", details: str = ""):
    user = request.user if (request and hasattr(request, "user") and request.user.is_authenticated) else None
    ip = get_client_ip(request) if request else None
    AuditLog.objects.create(
        user=user,
        action_type=action_type,
        target_model=target_model,
        target_id=str(target_id),
        details=details,
        ip_address=ip,
    )