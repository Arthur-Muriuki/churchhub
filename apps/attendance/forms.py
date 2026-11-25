from django import forms
from members.models import Member
from .models import AttendanceRecord


class AttendanceBatchForm(forms.Form):
    """
    Allows marking attendance across active members in one submission,
    plus updating any extra headcount for non-registered attendees.
    """
    additional_headcount = forms.IntegerField(
        min_value=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        label="Additional Headcount (Visitors / Walk-ins)",
    )

    def __init__(self, *args, event=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event
        members = Member.objects.filter(is_active=True, membership_status="ACTIVE").order_by("last_name", "first_name")
        existing_map = {
            rec.member_id: rec.status
            for rec in AttendanceRecord.objects.filter(event=event)
        } if event else {}

        for member in members:
            field_name = f"status_{member.member_id}"
            self.fields[field_name] = forms.ChoiceField(
                choices=[("NONE", "-- Not Marked --")] + list(AttendanceRecord.STATUS_CHOICES),
                initial=existing_map.get(member.member_id, "NONE"),
                required=False,
                widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
                label=member.full_name,
            )
            note_field = f"note_{member.member_id}"
            self.fields[note_field] = forms.CharField(
                required=False,
                widget=forms.TextInput(attrs={"class": "form-control form-control-sm", "placeholder": "Optional note"}),
            )

    def iter_member_rows(self):
        members = Member.objects.filter(is_active=True, membership_status="ACTIVE").order_by("last_name", "first_name")
        for member in members:
            yield {
                "member": member,
                "status_field": self[f"status_{member.member_id}"],
                "note_field": self[f"note_{member.member_id}"],
            }