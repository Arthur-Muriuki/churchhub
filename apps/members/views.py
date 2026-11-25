from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import role_permission_required
from accounts.utils import log_audit
from .forms import MemberForm
from .models import Member


@role_permission_required("members.view")
def member_list_view(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()
    show_archived = request.GET.get("archived") == "1" and request.user.has_role_perm("members.deactivate")

    members = Member.objects.filter(is_active=not show_archived)

    if status_filter:
        members = members.filter(membership_status=status_filter)

    if query:
        members = members.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(member_number__icontains=query)
            | Q(phone_number__icontains=query)
            | Q(email__icontains=query)
        )

    context = {
        "members": members,
        "query": query,
        "status_filter": status_filter,
        "show_archived": show_archived,
        "status_choices": Member.MEMBERSHIP_STATUS_CHOICES,
    }
    return render(request, "members/member_list.html", context)


@role_permission_required("members.add")
def member_create_view(request):
    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            log_audit(
                request=request,
                action_type="CREATE",
                target_model="Member",
                target_id=member.member_id,
                details=f"Registered member {member.full_name} ({member.member_number})",
            )
            messages.success(request, f"Member profile '{member.full_name}' created successfully.")
            return redirect("members:detail", pk=member.member_id)
        messages.error(request, "Please correct the validation errors below.")
    else:
        form = MemberForm()

    return render(request, "members/member_form.html", {"form": form, "mode": "create"})


@role_permission_required("members.view")
def member_detail_view(request, pk):
    member = get_object_or_404(Member, pk=pk)
    log_audit(
        request=request,
        action_type="VIEW_SENSITIVE",
        target_model="Member",
        target_id=member.member_id,
        details=f"Viewed member record for {member.full_name}",
    )
    return render(request, "members/member_detail.html", {"member": member})


@role_permission_required("members.change")
def member_update_view(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == "POST":
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            updated = form.save()
            log_audit(
                request=request,
                action_type="UPDATE",
                target_model="Member",
                target_id=updated.member_id,
                details=f"Updated member record for {updated.full_name} ({updated.member_number})",
            )
            messages.success(request, f"Member profile '{updated.full_name}' updated successfully.")
            return redirect("members:detail", pk=updated.member_id)
        messages.error(request, "Please correct the validation errors below.")
    else:
        form = MemberForm(instance=member)

    return render(request, "members/member_form.html", {"form": form, "member": member, "mode": "update"})


@role_permission_required("members.deactivate")
def member_soft_delete_view(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == "POST":
        member.is_active = False
        member.save(update_fields=["is_active", "updated_at"])
        log_audit(
            request=request,
            action_type="DELETE",
            target_model="Member",
            target_id=member.member_id,
            details=f"Soft-deleted member {member.full_name} ({member.member_number})",
        )
        messages.success(request, f"Member '{member.full_name}' has been archived (soft-deleted).")
        return redirect("members:list")

    return render(request, "members/member_confirm_delete.html", {"member": member})