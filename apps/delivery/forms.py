# tracker/forms.py
from django import forms
from .models import Company, Agent

class CompanyForm(forms.ModelForm):
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

class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = [
            "token",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "status",
        ]
