from django import forms
from .models import Department, DepartmentMembership


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "code", "description", "leader", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Auto-generated if blank"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "leader": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class DepartmentMembershipForm(forms.ModelForm):
    class Meta:
        model = DepartmentMembership
        fields = ["member", "role_title", "date_joined", "is_active"]
        widgets = {
            "member": forms.Select(attrs={"class": "form-select"}),
            "role_title": forms.Select(attrs={"class": "form-select"}),
            "date_joined": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["member"].queryset = self.fields["member"].queryset.filter(is_active=True)