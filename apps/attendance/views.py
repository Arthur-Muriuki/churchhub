from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import role_permission_required
from accounts.utils import log_audit
from events.models import Event
from members.models import Member
from .forms import AttendanceBatchForm
from .models import AttendanceRecord


@role_permission_required("attendance.record")
def mark_attendance_view(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    existing_records = {
        rec.member_id: rec
        for rec in AttendanceRecord.objects.filter(event=event)
    }

    if request.method == "POST":
        form = AttendanceBatchForm(request.POST, event=event)
        if form.is_valid():
            extra_count = form.cleaned_data.get("additional_headcount") or 0
            event.additional_headcount = extra_count
            event.save(update_fields=["additional_headcount", "updated_at"])

            active_members = Member.objects.filter(is_active=True, membership_status="ACTIVE")
            marked_count = 0

            for member in active_members:
                chosen_status = form.cleaned_data.get(f"status_{member.member_id}")
                note_val = form.cleaned_data.get(f"note_{member.member_id}", "").strip()

                if chosen_status and chosen_status != "NONE":
                    AttendanceRecord.objects.update_or_create(
                        event=event,
                        member=member,
                        defaults={
                            "status": chosen_status,
                            "notes": note_val,
                            "recorded_by": request.user,
                        },
                    )
                    marked_count += 1
                elif member.member_id in existing_records:
                    existing_records[member.member_id].delete()

            log_audit(
                request=request,
                action_type="UPDATE",
                target_model="AttendanceRecord",
                target_id=event.id,
                details=(
                    f"Recorded attendance for '{event.title}' ({event.event_date}): "
                    f"{marked_count} individual entries, +{extra_count} additional headcount."
                ),
            )
            messages.success(
                request,
                f"Attendance saved for '{event.title}'. Total attendance: {event.total_attendance}.",
            )
            return redirect("attendance:mark", event_id=event.id)
    else:
        initial_notes = {
            f"note_{rec.member_id}": rec.notes
            for rec in existing_records.values()
        }
        form = AttendanceBatchForm(
            event=event,
            initial={"additional_headcount": event.additional_headcount, **initial_notes},
        )

    records_list = AttendanceRecord.objects.filter(event=event).select_related("member", "recorded_by")
    context = {
        "event": event,
        "form": form,
        "records_list": records_list,
    }
    return render(request, "attendance/mark_attendance.html", context)