from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from .forms import ChurchHubLoginForm
from .utils import log_audit


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = ChurchHubLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        log_audit(
            request=self.request,
            action_type="LOGIN",
            target_model="User",
            target_id=self.request.user.id,
            details=f"User {self.request.user.username} logged in.",
        )
        messages.success(self.request, f"Welcome back, {self.request.user.get_full_name() or self.request.user.username}.")
        return response


class CustomLogoutView(LogoutView):
    next_page = "accounts:login"