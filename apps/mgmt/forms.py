# tracker/forms.py
from typing import Any
from django import forms
from mgmt.models import Company
from tracking.models import Recipient


class RecipientForm(forms.ModelForm[Recipient]):
    class Meta:
        model = Recipient
        fields = [
            "company",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "status",
            "tags",
        ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if "company" in self.fields and hasattr(self.fields["company"], "queryset"):
            self.fields["company"].queryset = Company.objects.all()
        return None


class CompanyForm(forms.ModelForm[Company]):
    class Meta:
        model = Company
        fields = [
            "name",
            "street_address",
            "city",
            "state",
            "zip_code",
            "country",
            "phone_number",
        ]
