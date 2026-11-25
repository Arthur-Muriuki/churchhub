from django import forms
from churches.models import ChurchProfile
from .models import Member


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            "member_number",
            "first_name",
            "middle_name",
            "last_name",
            "gender",
            "date_of_birth",
            "marital_status",
            "phone_number",
            "email",
            "residential_area",
            "postal_address",
            "emergency_contact_name",
            "emergency_contact_phone",
            "membership_status",
            "date_joined",
            "is_baptized",
            "baptism_date",
            "transfer_notes",
            "consent_given",
        ]
        widgets = {
            "member_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Auto-generated if blank"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "middle_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "marital_status": forms.Select(attrs={"class": "form-select"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "+254 7XX XXX XXX"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "residential_area": forms.TextInput(attrs={"class": "form-control"}),
            "postal_address": forms.TextInput(attrs={"class": "form-control"}),
            "emergency_contact_name": forms.TextInput(attrs={"class": "form-control"}),
            "emergency_contact_phone": forms.TextInput(attrs={"class": "form-control"}),
            "membership_status": forms.Select(attrs={"class": "form-select"}),
            "date_joined": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "is_baptized": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "baptism_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "transfer_notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "consent_given": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.church_profile = ChurchProfile.get_solo()
        if self.church_profile and self.church_profile.require_registration_consent:
            self.fields["consent_given"].required = True

    def clean(self):
        cleaned_data = super().clean()
        is_baptized = cleaned_data.get("is_baptized")
        baptism_date = cleaned_data.get("baptism_date")
        date_of_birth = cleaned_data.get("date_of_birth")

        if is_baptized and not baptism_date:
            self.add_error("baptism_date", "Please provide the baptism date when marked as baptized.")

        if date_of_birth and baptism_date and baptism_date < date_of_birth:
            self.add_error("baptism_date", "Baptism date cannot be earlier than date of birth.")

        if self.church_profile and self.church_profile.require_registration_consent:
            if not cleaned_data.get("consent_given"):
                self.add_error("consent_given", "Explicit data protection consent is required before saving.")

        return cleaned_data