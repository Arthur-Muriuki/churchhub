from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .utils import log_audit


def role_permission_required(perm_code: str):
    """
    Decorator enforcing RBAC permissions on views.
    Logs unauthorized attempts to AuditLog and raises PermissionDenied (403).
    """
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.has_role_perm(perm_code):
                return view_func(request, *args, **kwargs)

            log_audit(
                request=request,
                action_type="UNAUTHORIZED",
                target_model=view_func.__name__,
                details=f"Blocked access to {request.path} (Missing permission: {perm_code})",
            )
            raise PermissionDenied(f"Access Denied: Missing required privilege ({perm_code}).")

        return _wrapped_view
    return decorator