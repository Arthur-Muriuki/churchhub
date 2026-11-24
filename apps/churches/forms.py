from django import forms
from .models import ChurchProfile


class ChurchProfileForm(forms.ModelForm):
    class Meta:
        model = ChurchProfile
        fields = [
            "name",
            "short_name",
            "denomination",
            "motto",
            "logo",
            "official_stamp_or_signature",
            "email",
            "phone_number",
            "physical_address",
            "postal_address",
            "website",
            "service_schedule",
            "senior_pastor_name",
            "church_secretary_name",
            "certificate_footer_note",
            "enable_confidential_pastoral_notes",
            "require_registration_consent",
            "data_privacy_statement",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "short_name": forms.TextInput(attrs={"class": "form-control"}),
            "denomination": forms.TextInput(attrs={"class": "form-control"}),
            "motto": forms.TextInput(attrs={"class": "form-control"}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "official_stamp_or_signature": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "physical_address": forms.TextInput(attrs={"class": "form-control"}),
            "postal_address": forms.TextInput(attrs={"class": "form-control"}),
            "website": forms.URLInput(attrs={"class": "form-control"}),
            "service_schedule": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "senior_pastor_name": forms.TextInput(attrs={"class": "form-control"}),
            "church_secretary_name": forms.TextInput(attrs={"class": "form-control"}),
            "certificate_footer_note": forms.TextInput(attrs={"class": "form-control"}),
            "enable_confidential_pastoral_notes": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "require_registration_consent": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "data_privacy_statement": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }