from django import forms
from tracking.models import Agent, Campaign
from tracking.common import PublishingType, TrackingType


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = [
            'token',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'status',
        ]


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
    def clean_publishing_type(self):
        return self.cleaned_data['publishing_type'] or []

    def clean_ip_tracking(self):
        return self.cleaned_data['ip_tracking'] or []

    def clean_location_tracking(self):
        return self.cleaned_data['location_tracking'] or []

    def clean_locale_tracking(self):
        return self.cleaned_data['locale_tracking'] or []

    def clean_browser_tracking(self):
        return self.cleaned_data['browser_tracking'] or []

    def clean_time_tracking(self):
        return self.cleaned_data['time_tracking'] or []