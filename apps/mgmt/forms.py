# tracker/forms.py
from django import forms
from mgmt.models import Company


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
