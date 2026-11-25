from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import role_permission_required
from accounts.utils import log_audit
from churches.models import ChurchProfile
from .forms import BaptismRecordForm
from .models import BaptismRecord
from .pdf import generate_baptism_certificate_pdf


@role_permission_required("baptism.view")
def baptism_list_view(request):
    query = request.GET.get("q", "").strip()
    records = BaptismRecord.objects.select_related("member", "issued_by")

    if query:
        records = records.filter(
            Q(certificate_number__icontains=query)
            | Q(member__first_name__icontains=query)
            | Q(member__last_name__icontains=query)
            | Q(member__member_number__icontains=query)
            | Q(officiating_minister__icontains=query)
        )

    return render(request, "baptism/baptism_list.html", {"records": records, "query": query})


@role_permission_required("baptism.manage")
def baptism_create_view(request):
    if request.method == "POST":
        form = BaptismRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.issued_by = request.user
            record.save()
            log_audit(
                request=request,
                action_type="CREATE",
                target_model="BaptismRecord",
                target_id=record.id,
                details=f"Recorded baptism {record.certificate_number} for {record.member.full_name}",
            )
            messages.success(
                request,
                f"Baptism record '{record.certificate_number}' saved for {record.member.full_name}.",
            )
            return redirect("baptism:list")
    else:
        form = BaptismRecordForm()

    return render(request, "baptism/baptism_form.html", {"form": form, "mode": "create"})


@role_permission_required("baptism.manage")
def baptism_update_view(request, pk):
    record = get_object_or_404(BaptismRecord, pk=pk)
    if request.method == "POST":
        form = BaptismRecordForm(request.POST, instance=record)
        if form.is_valid():
            updated = form.save()
            log_audit(
                request=request,
                action_type="UPDATE",
                target_model="BaptismRecord",
                target_id=updated.id,
                details=f"Updated baptism record {updated.certificate_number}",
            )
            messages.success(request, f"Baptism record '{updated.certificate_number}' updated.")
            return redirect("baptism:list")
    else:
        form = BaptismRecordForm(instance=record)

    return render(request, "baptism/baptism_form.html", {"form": form, "record": record, "mode": "update"})


@role_permission_required("baptism.generate_certificate")
def baptism_certificate_pdf_view(request, pk):
    record = get_object_or_404(BaptismRecord.objects.select_related("member"), pk=pk)
    if not record.is_verified:
        messages.error(request, "Only officially verified baptism records can generate certificates.")
        return redirect("baptism:list")

    church_profile = ChurchProfile.get_solo()
    pdf_bytes = generate_baptism_certificate_pdf(record, church_profile)

    log_audit(
        request=request,
        action_type="EXPORT",
        target_model="BaptismCertificatePDF",
        target_id=record.certificate_number,
        details=f"Generated baptism certificate PDF for {record.member.full_name} ({record.certificate_number})",
    )

    filename = f"Baptism_Certificate_{record.certificate_number}.pdf"
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response