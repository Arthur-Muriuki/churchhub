from django import forms
from .models import Ministry, MinistryActivity


class MinistryForm(forms.ModelForm):
    class Meta:
        model = Ministry
        fields = ["name", "department", "leader", "meeting_schedule", "description", "members", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "leader": forms.Select(attrs={"class": "form-select"}),
            "meeting_schedule": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Saturdays 2:00 PM"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "members": forms.SelectMultiple(attrs={"class": "form-select", "size": 6}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["members"].queryset = self.fields["members"].queryset.filter(is_active=True)


class MinistryActivityForm(forms.ModelForm):
    class Meta:
        model = MinistryActivity
        fields = ["ministry", "title", "activity_date", "location", "attendance_count", "notes"]
        widgets = {
            "ministry": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "activity_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "attendance_count": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }