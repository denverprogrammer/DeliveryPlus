from django import forms
from tracking.models import Agent, Campaign
from tracking.common import PublishingType, TrackingType
from typing import Any


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = [
            'campaign',
            'token',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'status',
        ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if 'campaign' in self.fields:
            self.fields['campaign'].queryset = Campaign.objects.all()


class CampaignAdminForm(forms.ModelForm):
    publishing_type = forms.MultipleChoiceField(
        choices=PublishingType.choices(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    ip_tracking = forms.MultipleChoiceField(
        choices=TrackingType.choices(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    location_tracking = forms.MultipleChoiceField(
        choices=TrackingType.choices(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    locale_tracking = forms.MultipleChoiceField(
        choices=TrackingType.choices(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    browser_tracking = forms.MultipleChoiceField(
        choices=TrackingType.choices(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    time_tracking = forms.MultipleChoiceField(
        choices=TrackingType.choices(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Campaign
        fields = '__all__'

    # Clean methods to ensure JSON is stored properly
    def clean_publishing_type(self) -> list[str]:
        return self.cleaned_data['publishing_type'] or []

    def clean_ip_tracking(self) -> list[str]:
        return self.cleaned_data['ip_tracking'] or []

    def clean_location_tracking(self) -> list[str]:
        return self.cleaned_data['location_tracking'] or []

    def clean_locale_tracking(self) -> list[str]:
        return self.cleaned_data['locale_tracking'] or []

    def clean_browser_tracking(self) -> list[str]:
        return self.cleaned_data['browser_tracking'] or []

    def clean_time_tracking(self) -> list[str]:
        return self.cleaned_data['time_tracking'] or []


class TrackingDataViewForm(forms.Form):
    """Form for displaying tracking data in a readonly format."""
    server_timestamp = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'readonly': True})
    )
    http_method = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    ip_address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    ip_source = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    os = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    browser = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    platform = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    locale = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    client_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'readonly': True})
    )
    client_timezone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': True})
    )
    latitude = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={'readonly': True})
    )
    longitude = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={'readonly': True})
    )
    location_source = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'readonly': True})
    )
