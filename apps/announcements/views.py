from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from accounts.decorators import role_permission_required
from accounts.utils import log_audit
from .forms import AnnouncementForm
from .models import Announcement, AnnouncementReadReceipt


@role_permission_required("announcements.view")
def announcement_list_view(request):
    today = timezone.localdate()
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    include_drafts = request.GET.get("all") == "1" and request.user.has_role_perm("announcements.manage")

    qs = Announcement.objects.select_related(
        "target_department", "target_ministry", "created_by"
    ).prefetch_related("read_by")

    if not include_drafts:
        qs = qs.filter(is_published=True, publish_date__lte=today).filter(
            Q(expires_on__isnull=True) | Q(expires_on__gte=today)
        )

    if category:
        qs = qs.filter(category=category)

    if query:
        qs = qs.filter(
            Q(title__icontains=query)
            | Q(body__icontains=query)
            | Q(target_department__name__icontains=query)
            | Q(target_ministry__name__icontains=query)
        )

    read_ids = set(
        AnnouncementReadReceipt.objects.filter(user=request.user).values_list("announcement_id", flat=True)
    )

    items = [
        {
            "announcement": ann,
            "is_read": ann.id in read_ids,
            "read_count": ann.read_by.count(),
        }
        for ann in qs
    ]

    context = {
        "items": items,
        "query": query,
        "category": category,
        "include_drafts": include_drafts,
        "category_choices": Announcement.CATEGORY_CHOICES,
    }
    return render(request, "announcements/announcement_list.html", context)


@role_permission_required("announcements.manage")
def announcement_create_view(request):
    if request.method == "POST":
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            ann = form.save(commit=False)
            ann.created_by = request.user
            ann.save()
            log_audit(
                request=request,
                action_type="CREATE",
                target_model="Announcement",
                target_id=ann.id,
                details=f"Published announcement '{ann.title}' ({ann.get_category_display()})",
            )
            messages.success(request, f"Announcement '{ann.title}' saved.")
            return redirect("announcements:list")
    else:
        form = AnnouncementForm()

    return render(request, "announcements/announcement_form.html", {"form": form, "mode": "create"})


@role_permission_required("announcements.manage")
def announcement_update_view(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    if request.method == "POST":
        form = AnnouncementForm(request.POST, instance=ann)
        if form.is_valid():
            updated = form.save()
            log_audit(
                request=request,
                action_type="UPDATE",
                target_model="Announcement",
                target_id=updated.id,
                details=f"Updated announcement '{updated.title}'",
            )
            messages.success(request, f"Announcement '{updated.title}' updated.")
            return redirect("announcements:list")
    else:
        form = AnnouncementForm(instance=ann)

    return render(request, "announcements/announcement_form.html", {"form": form, "announcement": ann, "mode": "update"})


@role_permission_required("announcements.view")
def announcement_mark_read_view(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    if request.method == "POST":
        AnnouncementReadReceipt.objects.get_or_create(announcement=ann, user=request.user)
        messages.success(request, f"Marked '{ann.title}' as read.")
    return redirect("announcements:list")