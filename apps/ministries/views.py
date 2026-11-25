from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import role_permission_required
from accounts.utils import log_audit
from .forms import MinistryActivityForm, MinistryForm
from .models import Ministry, MinistryActivity


@role_permission_required("departments.view")
def ministry_list_view(request):
    ministries = Ministry.objects.select_related("department", "leader").prefetch_related("members")
    activities = MinistryActivity.objects.select_related("ministry", "recorded_by")[:10]
    return render(
        request,
        "ministries/ministry_list.html",
        {"ministries": ministries, "activities": activities},
    )


@role_permission_required("departments.manage")
def ministry_create_view(request):
    if request.method == "POST":
        form = MinistryForm(request.POST)
        if form.is_valid():
            ministry = form.save()
            log_audit(
                request=request,
                action_type="CREATE",
                target_model="Ministry",
                target_id=ministry.id,
                details=f"Created ministry {ministry.name}",
            )
            messages.success(request, f"Ministry '{ministry.name}' created.")
            return redirect("ministries:list")
    else:
        form = MinistryForm()
    return render(request, "ministries/ministry_form.html", {"form": form, "mode": "create"})


@role_permission_required("departments.manage")
def ministry_update_view(request, pk):
    ministry = get_object_or_404(Ministry, pk=pk)
    if request.method == "POST":
        form = MinistryForm(request.POST, instance=ministry)
        if form.is_valid():
            updated = form.save()
            log_audit(
                request=request,
                action_type="UPDATE",
                target_model="Ministry",
                target_id=updated.id,
                details=f"Updated ministry {updated.name}",
            )
            messages.success(request, f"Ministry '{updated.name}' updated.")
            return redirect("ministries:list")
    else:
        form = MinistryForm(instance=ministry)
    return render(request, "ministries/ministry_form.html", {"form": form, "ministry": ministry, "mode": "update"})


@role_permission_required("departments.manage_own")
def activity_create_view(request):
    if request.method == "POST":
        form = MinistryActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.recorded_by = request.user
            activity.save()
            log_audit(
                request=request,
                action_type="CREATE",
                target_model="MinistryActivity",
                target_id=activity.id,
                details=f"Logged activity '{activity.title}' for {activity.ministry.name}",
            )
            messages.success(request, f"Activity '{activity.title}' recorded.")
            return redirect("ministries:list")
    else:
        form = MinistryActivityForm()
    return render(request, "ministries/activity_form.html", {"form": form})