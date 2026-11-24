from django.contrib import messages
from django.shortcuts import redirect, render
from accounts.decorators import role_permission_required
from accounts.utils import log_audit
from .forms import ChurchProfileForm
from .models import ChurchProfile


@role_permission_required("churches.manage_settings")
def church_settings_view(request):
    profile = ChurchProfile.get_solo()
    if request.method == "POST":
        form = ChurchProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            updated_profile = form.save()
            log_audit(
                request=request,
                action_type="UPDATE",
                target_model="ChurchProfile",
                target_id=updated_profile.id,
                details=f"Updated church profile & system settings for {updated_profile.name}",
            )
            messages.success(request, "Church profile and system settings updated successfully.")
            return redirect("churches:settings")
    else:
        form = ChurchProfileForm(instance=profile)

    return render(request, "churches/settings.html", {"form": form, "profile": profile})