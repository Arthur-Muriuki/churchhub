import csv
import json
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from accounts.decorators import role_permission_required
from accounts.utils import log_audit
from attendance.models import AttendanceRecord
from baptism.models import BaptismRecord
from departments.models import Department
from events.models import Event
from members.models import Member
from ministries.models import Ministry
from pastoral.models import PastoralCareLog
from visitors.models import Visitor


def _parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


@login_required
def dashboard_view(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)

    active_members_qs = Member.objects.filter(is_active=True)
    total_members = active_members_qs.count()
    active_status_members = active_members_qs.filter(membership_status="ACTIVE").count()
    new_members_this_month = active_members_qs.filter(date_joined__gte=month_start).count()
    baptized_count = active_members_qs.filter(is_baptized=True).count()
    total_baptisms = BaptismRecord.objects.filter(is_verified=True).count()
    open_visitors = Visitor.objects.exclude(status__in=["INTEGRATED", "CLOSED"]).count()
    active_pastoral_cases = PastoralCareLog.objects.exclude(status="RESOLVED").count()

    # Recent events & attendance trend data for Chart.js (last 8 events)
    recent_events = list(
        Event.objects.prefetch_related("attendance_records").order_by("-event_date", "-created_at")[:8]
    )
    recent_events.reverse()

    event_labels = [f"{ev.event_date:%b %d} - {ev.title[:18]}" for ev in recent_events]
    event_totals = [ev.total_attendance for ev in recent_events]
    avg_attendance = round(sum(event_totals) / len(event_totals), 1) if event_totals else 0

    # Department distribution for Chart.js
    departments = list(
        Department.objects.filter(is_active=True)
        .annotate(roster_count=Count("memberships", filter=Q(memberships__is_active=True)))
        .order_by("-roster_count", "name")
    )
    dept_labels = [d.name for d in departments]
    dept_counts = [d.roster_count for d in departments]

    context = {
        "total_members": total_members,
        "active_status_members": active_status_members,
        "new_members_this_month": new_members_this_month,
        "baptized_count": baptized_count,
        "total_baptisms": total_baptisms,
        "open_visitors": open_visitors,
        "active_pastoral_cases": active_pastoral_cases,
        "avg_attendance": avg_attendance,
        "recent_events": list(reversed(recent_events)),
        "departments": departments,
        "event_labels_json": json.dumps(event_labels),
        "event_totals_json": json.dumps(event_totals),
        "dept_labels_json": json.dumps(dept_labels),
        "dept_counts_json": json.dumps(dept_counts),
    }
    return render(request, "reports/dashboard.html", context)


def _get_filtered_report_rows(report_type, start_date, end_date):
    if report_type == "attendance":
        qs = Event.objects.select_related("department", "ministry").prefetch_related("attendance_records")
        if start_date:
            qs = qs.filter(event_date__gte=start_date)
        if end_date:
            qs = qs.filter(event_date__lte=end_date)
        headers = ["Event Date", "Event Title", "Event Type", "Present Members", "Additional Headcount", "Total Attendance"]
        rows = [
            [
                ev.event_date.isoformat(),
                ev.title,
                ev.get_event_type_display(),
                ev.present_members_count,
                ev.additional_headcount,
                ev.total_attendance,
            ]
            for ev in qs.order_by("-event_date")
        ]
        return headers, rows

    if report_type == "baptisms":
        qs = BaptismRecord.objects.select_related("member")
        if start_date:
            qs = qs.filter(baptism_date__gte=start_date)
        if end_date:
            qs = qs.filter(baptism_date__lte=end_date)
        headers = ["Certificate No.", "Member Name", "Member ID", "Baptism Date", "Minister", "Venue", "Verified"]
        rows = [
            [
                rec.certificate_number,
                rec.member.full_name,
                rec.member.member_number,
                rec.baptism_date.isoformat(),
                rec.officiating_minister,
                rec.location_or_venue,
                "Yes" if rec.is_verified else "No",
            ]
            for rec in qs.order_by("-baptism_date")
        ]
        return headers, rows

    if report_type == "departments":
        dept_qs = Department.objects.select_related("leader").annotate(
            active_members=Count("memberships", filter=Q(memberships__is_active=True))
        )
        headers = ["Type", "Name", "Leader", "Member / Roster Count", "Status"]
        rows = [
            [
                "Department",
                d.name,
                d.leader.get_full_name() or d.leader.username if d.leader else "Unassigned",
                d.active_members,
                "Active" if d.is_active else "Inactive",
            ]
            for d in dept_qs
        ]
        for m in Ministry.objects.select_related("department", "leader").prefetch_related("members"):
            rows.append([
                "Ministry",
                f"{m.name} ({m.department.name})" if m.department else m.name,
                m.leader.get_full_name() or m.leader.username if m.leader else "Unassigned",
                m.members.count(),
                "Active" if m.is_active else "Inactive",
            ])
        return headers, rows

    if report_type == "visitors":
        qs = Visitor.objects.select_related("assigned_to")
        if start_date:
            qs = qs.filter(visit_date__gte=start_date)
        if end_date:
            qs = qs.filter(visit_date__lte=end_date)
        headers = ["Visit Date", "Visitor Name", "Phone", "Status", "Assigned To", "Next Follow-Up"]
        rows = [
            [
                v.visit_date.isoformat(),
                v.full_name,
                v.phone_number,
                v.get_status_display(),
                v.assigned_to.get_full_name() or v.assigned_to.username if v.assigned_to else "Unassigned",
                v.next_followup_date.isoformat() if v.next_followup_date else "",
            ]
            for v in qs.order_by("-visit_date")
        ]
        return headers, rows

    # Default: members
    qs = Member.objects.filter(is_active=True)
    if start_date:
        qs = qs.filter(date_joined__gte=start_date)
    if end_date:
        qs = qs.filter(date_joined__lte=end_date)
    headers = ["Member ID", "Full Name", "Gender", "Phone", "Email", "Status", "Baptized", "Date Joined"]
    rows = [
        [
            m.member_number,
            m.full_name,
            m.get_gender_display(),
            m.phone_number,
            m.email,
            m.get_membership_status_display(),
            "Yes" if m.is_baptized else "No",
            m.date_joined.isoformat(),
        ]
        for m in qs.order_by("last_name", "first_name")
    ]
    return headers, rows


@role_permission_required("reports.view_dashboard")
def report_center_view(request):
    report_type = request.GET.get("type", "members").strip()
    if report_type not in {"members", "attendance", "baptisms", "departments", "visitors"}:
        report_type = "members"

    start_str = request.GET.get("start_date", "").strip()
    end_str = request.GET.get("end_date", "").strip()
    start_date = _parse_date(start_str)
    end_date = _parse_date(end_str)

    headers, rows = _get_filtered_report_rows(report_type, start_date, end_date)

    context = {
        "report_type": report_type,
        "start_date": start_str,
        "end_date": end_str,
        "headers": headers,
        "rows": rows,
        "row_count": len(rows),
    }
    return render(request, "reports/report_center.html", context)


@role_permission_required("reports.export")
def export_report_csv_view(request):
    report_type = request.GET.get("type", "members").strip()
    if report_type not in {"members", "attendance", "baptisms", "departments", "visitors"}:
        report_type = "members"

    start_str = request.GET.get("start_date", "").strip()
    end_str = request.GET.get("end_date", "").strip()
    start_date = _parse_date(start_str)
    end_date = _parse_date(end_str)

    headers, rows = _get_filtered_report_rows(report_type, start_date, end_date)

    log_audit(
        request=request,
        action_type="EXPORT",
        target_model="ReportExportCSV",
        target_id=report_type,
        details=f"Exported '{report_type}' CSV report ({len(rows)} rows; range: {start_str or 'all'} to {end_str or 'all'})",
    )

    filename = f"churchhub_{report_type}_report_{timezone.localdate().isoformat()}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(headers)
    writer.writerows(rows)
    return response