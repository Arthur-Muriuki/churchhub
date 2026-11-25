from django import forms
from .models import Visitor, VisitorFollowUp


class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = [
            "full_name",
            "phone_number",
            "email",
            "residential_area",
            "visit_date",
            "visited_event",
            "how_heard",
            "status",
            "assigned_to",
            "next_followup_date",
            "prayer_or_notes",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "+254 7XX XXX XXX"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "residential_area": forms.TextInput(attrs={"class": "form-control"}),
            "visit_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "visited_event": forms.Select(attrs={"class": "form-select"}),
            "how_heard": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
            "next_followup_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "prayer_or_notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class VisitorFollowUpForm(forms.ModelForm):
    class Meta:
        model = VisitorFollowUp
        fields = ["contact_date", "channel", "summary", "next_action_date"]
        widgets = {
            "contact_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "channel": forms.Select(attrs={"class": "form-select"}),
            "summary": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "next_action_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }