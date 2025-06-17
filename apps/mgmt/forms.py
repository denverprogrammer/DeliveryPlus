# tracker/forms.py
from typing import Any
from django import forms
from mgmt.models import Company
from tracking.models import Agent
from tracking.models import Campaign


class AgentForm(forms.ModelForm[Agent]):
    class Meta:
        model = Agent
        fields = [
            "campaign",
            "token",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "status",
        ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if "campaign" in self.fields and hasattr(self.fields["campaign"], "queryset"):
            self.fields["campaign"].queryset = Campaign.objects.all()


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
