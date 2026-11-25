from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import role_permission_required
from accounts.utils import log_audit
from .forms import VisitorFollowUpForm, VisitorForm
from .models import Visitor


@role_permission_required("visitors.view")
def visitor_list_view(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()
    visitors = Visitor.objects.select_related("visited_event", "assigned_to").prefetch_related("followups")

    if status_filter:
        visitors = visitors.filter(status=status_filter)

    if query:
        visitors = visitors.filter(
            Q(full_name__icontains=query)
            | Q(phone_number__icontains=query)
            | Q(email__icontains=query)
            | Q(residential_area__icontains=query)
        )

    context = {
        "visitors": visitors,
        "query": query,
        "status_filter": status_filter,
        "status_choices": Visitor.STATUS_CHOICES,
    }
    return render(request, "visitors/visitor_list.html", context)


@role_permission_required("visitors.manage")
def visitor_create_view(request):
    if request.method == "POST":
        form = VisitorForm(request.POST)
        if form.is_valid():
            visitor = form.save(commit=False)
            visitor.created_by = request.user
            visitor.save()
            log_audit(
                request=request,
                action_type="CREATE",
                target_model="Visitor",
                target_id=visitor.id,
                details=f"Registered visitor '{visitor.full_name}' ({visitor.visit_date})",
            )
            messages.success(request, f"Visitor '{visitor.full_name}' registered successfully.")
            return redirect("visitors:detail", pk=visitor.id)
    else:
        form = VisitorForm()

    return render(request, "visitors/visitor_form.html", {"form": form, "mode": "create"})


@role_permission_required("visitors.view")
def visitor_detail_view(request, pk):
    visitor = get_object_or_404(
        Visitor.objects.select_related("visited_event", "assigned_to", "converted_member"),
        pk=pk,
    )
    followups = visitor.followups.select_related("recorded_by")

    if request.method == "POST":
        if not request.user.has_role_perm("visitors.manage"):
            messages.error(request, "You do not have permission to log follow-up actions.")
            return redirect("visitors:detail", pk=visitor.id)

        followup_form = VisitorFollowUpForm(request.POST)
        if followup_form.is_valid():
            followup = followup_form.save(commit=False)
            followup.visitor = visitor
            followup.recorded_by = request.user
            followup.save()

            if followup.next_action_date:
                visitor.next_followup_date = followup.next_action_date
            if visitor.status == "NEW":
                visitor.status = "CONTACTED"
            visitor.save(update_fields=["next_followup_date", "status", "updated_at"])

            log_audit(
                request=request,
                action_type="CREATE",
                target_model="VisitorFollowUp",
                target_id=followup.id,
                details=f"Logged {followup.get_channel_display()} follow-up for {visitor.full_name}",
            )
            messages.success(request, "Follow-up activity recorded.")
            return redirect("visitors:detail", pk=visitor.id)
    else:
        followup_form = VisitorFollowUpForm()

    return render(
        request,
        "visitors/visitor_detail.html",
        {"visitor": visitor, "followups": followups, "followup_form": followup_form},
    )


@role_permission_required("visitors.manage")
def visitor_update_view(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    if request.method == "POST":
        form = VisitorForm(request.POST, instance=visitor)
        if form.is_valid():
            updated = form.save()
            log_audit(
                request=request,
                action_type="UPDATE",
                target_model="Visitor",
                target_id=updated.id,
                details=f"Updated visitor '{updated.full_name}'",
            )
            messages.success(request, f"Visitor '{updated.full_name}' updated.")
            return redirect("visitors:detail", pk=updated.id)
    else:
        form = VisitorForm(instance=visitor)

    return render(request, "visitors/visitor_form.html", {"form": form, "visitor": visitor, "mode": "update"})