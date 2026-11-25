from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "event_type",
            "event_date",
            "start_time",
            "end_time",
            "location",
            "department",
            "ministry",
            "additional_headcount",
            "is_completed",
            "description",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Sunday First Service"}),
            "event_type": forms.Select(attrs={"class": "form-select"}),
            "event_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Main Sanctuary"}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "ministry": forms.Select(attrs={"class": "form-select"}),
            "additional_headcount": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "is_completed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }