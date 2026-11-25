from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import role_permission_required
from accounts.utils import log_audit
from .forms import EventForm
from .models import Event


@role_permission_required("events.view")
def event_list_view(request):
    query = request.GET.get("q", "").strip()
    event_type = request.GET.get("type", "").strip()
    events = Event.objects.select_related("department", "ministry", "created_by").prefetch_related("attendance_records")

    if event_type:
        events = events.filter(event_type=event_type)

    if query:
        events = events.filter(
            Q(title__icontains=query)
            | Q(location__icontains=query)
            | Q(department__name__icontains=query)
            | Q(ministry__name__icontains=query)
        )

    context = {
        "events": events,
        "query": query,
        "event_type": event_type,
        "type_choices": Event.EVENT_TYPE_CHOICES,
    }
    return render(request, "events/event_list.html", context)


@role_permission_required("events.manage")
def event_create_view(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            log_audit(
                request=request,
                action_type="CREATE",
                target_model="Event",
                target_id=event.id,
                details=f"Scheduled event '{event.title}' on {event.event_date}",
            )
            messages.success(request, f"Event '{event.title}' created successfully.")
            return redirect("attendance:mark", event_id=event.id)
    else:
        form = EventForm()

    return render(request, "events/event_form.html", {"form": form, "mode": "create"})


@role_permission_required("events.manage")
def event_update_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            updated = form.save()
            log_audit(
                request=request,
                action_type="UPDATE",
                target_model="Event",
                target_id=updated.id,
                details=f"Updated event '{updated.title}'",
            )
            messages.success(request, f"Event '{updated.title}' updated.")
            return redirect("events:list")
    else:
        form = EventForm(instance=event)

    return render(request, "events/event_form.html", {"form": form, "event": event, "mode": "update"})