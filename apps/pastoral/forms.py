from django import forms
from members.models import Member
from .models import PastoralCareLog


class PastoralCareLogForm(forms.ModelForm):
    confidential_notes = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Enter confidential session notes (encrypted with AES-256/Fernet before saving)...",
            }
        ),
        label="Confidential Pastoral / Counselling Notes",
    )

    class Meta:
        model = PastoralCareLog
        fields = [
            "member",
            "category",
            "status",
            "session_date",
            "follow_up_date",
            "confidential_notes",
        ]
        widgets = {
            "member": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "session_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "follow_up_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["member"].queryset = Member.objects.filter(is_active=True).order_by("last_name", "first_name")
        if self.instance and self.instance.pk:
            self.fields["confidential_notes"].initial = self.instance.get_confidential_notes()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.set_confidential_notes(self.cleaned_data["confidential_notes"])
        if commit:
            instance.save()
        return instance