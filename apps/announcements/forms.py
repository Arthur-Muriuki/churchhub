from django import forms
from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = [
            "title",
            "category",
            "priority",
            "publish_date",
            "expires_on",
            "target_department",
            "target_ministry",
            "body",
            "is_pinned",
            "is_published",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Sunday Combined Service & Baptism"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "publish_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "expires_on": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "target_department": forms.Select(attrs={"class": "form-select"}),
            "target_ministry": forms.Select(attrs={"class": "form-select"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "is_pinned": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        publish_date = cleaned_data.get("publish_date")
        expires_on = cleaned_data.get("expires_on")

        if publish_date and expires_on and expires_on < publish_date:
            self.add_error("expires_on", "Expiration date cannot be earlier than the publish date.")

        return cleaned_data