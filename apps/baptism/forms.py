from django import forms
from members.models import Member
from .models import BaptismRecord


class BaptismRecordForm(forms.ModelForm):
    class Meta:
        model = BaptismRecord
        fields = [
            "member",
            "baptism_date",
            "officiating_minister",
            "location_or_venue",
            "witness_name",
            "is_verified",
            "notes",
        ]
        widgets = {
            "member": forms.Select(attrs={"class": "form-select"}),
            "baptism_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "officiating_minister": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Rev. / Pastor Full Name"}),
            "location_or_venue": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Main Sanctuary / River / Baptistery"}),
            "witness_name": forms.TextInput(attrs={"class": "form-control"}),
            "is_verified": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["member"].queryset = Member.objects.filter(is_active=True).order_by("last_name", "first_name")

    def clean(self):
        cleaned_data = super().clean()
        member = cleaned_data.get("member")
        baptism_date = cleaned_data.get("baptism_date")

        if member and member.date_of_birth and baptism_date and baptism_date < member.date_of_birth:
            self.add_error("baptism_date", "Baptism date cannot be earlier than the member's date of birth.")

        return cleaned_data