from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import role_permission_required
from accounts.utils import log_audit
from .forms import DepartmentForm, DepartmentMembershipForm
from .models import Department, DepartmentMembership


@role_permission_required("departments.view")
def department_list_view(request):
    departments = Department.objects.select_related("leader").prefetch_related("memberships")
    return render(request, "departments/department_list.html", {"departments": departments})


@role_permission_required("departments.manage")
def department_create_view(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            log_audit(
                request=request,
                action_type="CREATE",
                target_model="Department",
                target_id=dept.id,
                details=f"Created department {dept.name}",
            )
            messages.success(request, f"Department '{dept.name}' created successfully.")
            return redirect("departments:detail", pk=dept.id)
    else:
        form = DepartmentForm()
    return render(request, "departments/department_form.html", {"form": form, "mode": "create"})


@role_permission_required("departments.view")
def department_detail_view(request, pk):
    department = get_object_or_404(Department.objects.select_related("leader"), pk=pk)
    memberships = department.memberships.select_related("member")

    can_manage_roster = (
        request.user.has_role_perm("departments.manage")
        or (request.user.has_role_perm("departments.manage_own") and department.leader == request.user)
    )

    if request.method == "POST" and can_manage_roster:
        form = DepartmentMembershipForm(request.POST)
        if form.is_valid():
            member = form.cleaned_data["member"]
            membership, created = DepartmentMembership.objects.update_or_create(
                department=department,
                member=member,
                defaults={
                    "role_title": form.cleaned_data["role_title"],
                    "date_joined": form.cleaned_data["date_joined"],
                    "is_active": form.cleaned_data["is_active"],
                },
            )
            log_audit(
                request=request,
                action_type="CREATE" if created else "UPDATE",
                target_model="DepartmentMembership",
                target_id=membership.id,
                details=f"{'Added' if created else 'Updated'} {member.full_name} in {department.name}",
            )
            messages.success(request, f"Updated roster entry for {member.full_name}.")
            return redirect("departments:detail", pk=department.id)
    else:
        form = DepartmentMembershipForm()

    context = {
        "department": department,
        "memberships": memberships,
        "form": form,
        "can_manage_roster": can_manage_roster,
    }
    return render(request, "departments/department_detail.html", context)


@role_permission_required("departments.manage")
def department_update_view(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == "POST":
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            dept = form.save()
            log_audit(
                request=request,
                action_type="UPDATE",
                target_model="Department",
                target_id=dept.id,
                details=f"Updated department {dept.name}",
            )
            messages.success(request, f"Department '{dept.name}' updated.")
            return redirect("departments:detail", pk=dept.id)
    else:
        form = DepartmentForm(instance=department)
    return render(request, "departments/department_form.html", {"form": form, "department": department, "mode": "update"})