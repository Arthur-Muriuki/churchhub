from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import role_permission_required
from accounts.utils import log_audit
from churches.models import ChurchProfile
from .forms import PastoralCareLogForm
from .models import PastoralCareLog


@role_permission_required("pastoral.view_confidential")
def pastoral_list_view(request):
    church_profile = ChurchProfile.get_solo()
    if church_profile and not church_profile.enable_confidential_pastoral_notes:
        messages.warning(
            request,
            "Confidential pastoral care notes are currently disabled in Church Settings.",
        )
        return render(request, "pastoral/pastoral_disabled.html", {"church_profile": church_profile})

    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()
    logs = PastoralCareLog.objects.select_related("member", "pastor")

    if status_filter:
        logs = logs.filter(status=status_filter)

    if query:
        logs = logs.filter(
            Q(member__first_name__icontains=query)
            | Q(member__last_name__icontains=query)
            | Q(member__member_number__icontains=query)
        )

    log_audit(
        request=request,
        action_type="VIEW_SENSITIVE",
        target_model="PastoralCareLog",
        details="Viewed confidential pastoral care log index",
    )

    items = [
        {
            "log": entry,
            "decrypted_notes": entry.get_confidential_notes(),
        }
        for entry in logs
    ]

    context = {
        "items": items,
        "query": query,
        "status_filter": status_filter,
        "status_choices": PastoralCareLog.STATUS_CHOICES,
    }
    return render(request, "pastoral/pastoral_list.html", context)


@role_permission_required("pastoral.manage_confidential")
def pastoral_create_view(request):
    church_profile = ChurchProfile.get_solo()
    if church_profile and not church_profile.enable_confidential_pastoral_notes:
        messages.warning(request, "Confidential pastoral care notes are disabled in Church Settings.")
        return redirect("pastoral:list")

    if request.method == "POST":
        form = PastoralCareLogForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.pastor = request.user
            entry.save()
            log_audit(
                request=request,
                action_type="CREATE",
                target_model="PastoralCareLog",
                target_id=entry.id,
                details=f"Created encrypted pastoral care entry for member {entry.member.member_number}",
            )
            messages.success(request, "Confidential pastoral care log encrypted and saved.")
            return redirect("pastoral:list")
    else:
        form = PastoralCareLogForm()

    return render(request, "pastoral/pastoral_form.html", {"form": form, "mode": "create"})


@role_permission_required("pastoral.manage_confidential")
def pastoral_update_view(request, pk):
    entry = get_object_or_404(PastoralCareLog, pk=pk)
    if request.method == "POST":
        form = PastoralCareLogForm(request.POST, instance=entry)
        if form.is_valid():
            updated = form.save()
            log_audit(
                request=request,
                action_type="UPDATE",
                target_model="PastoralCareLog",
                target_id=updated.id,
                details=f"Updated encrypted pastoral care entry for member {updated.member.member_number}",
            )
            messages.success(request, "Confidential pastoral care log updated.")
            return redirect("pastoral:list")
    else:
        form = PastoralCareLogForm(instance=entry)

    return render(request, "pastoral/pastoral_form.html", {"form": form, "entry": entry, "mode": "update"})