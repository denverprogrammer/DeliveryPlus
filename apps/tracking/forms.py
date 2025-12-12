from common.enums import PublishingType
from common.enums import TrackingType
from dal import autocomplete
from django import forms

# from taggit.forms import TagWidget
from django_select2.forms import ModelSelect2TagWidget
from taggit.models import Tag
from tracking.models import Campaign
from tracking.models import Recipient
from tracking.models import Tracking


class CampaignSubAdminForm(forms.ModelForm[Campaign]):
    publishing_type = forms.MultipleChoiceField(
        choices=PublishingType.choices(), required=False, widget=forms.CheckboxSelectMultiple
    )
    ip_tracking = forms.MultipleChoiceField(
        choices=TrackingType.choices(), required=False, widget=forms.CheckboxSelectMultiple
    )
    location_tracking = forms.MultipleChoiceField(
        choices=TrackingType.choices(), required=False, widget=forms.CheckboxSelectMultiple
    )
    locale_tracking = forms.MultipleChoiceField(
        choices=TrackingType.choices(), required=False, widget=forms.CheckboxSelectMultiple
    )
    browser_tracking = forms.MultipleChoiceField(
        choices=TrackingType.choices(), required=False, widget=forms.CheckboxSelectMultiple
    )
    time_tracking = forms.MultipleChoiceField(
        choices=TrackingType.choices(), required=False, widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Campaign
        fields = "__all__"

    # Clean methods to ensure JSON is stored properly
    def clean_publishing_type(self) -> list[str]:
        return self.cleaned_data["publishing_type"] or []

    def clean_ip_tracking(self) -> list[str]:
        return self.cleaned_data["ip_tracking"] or []

    def clean_location_tracking(self) -> list[str]:
        return self.cleaned_data["location_tracking"] or []

    def clean_locale_tracking(self) -> list[str]:
        return self.cleaned_data["locale_tracking"] or []

    def clean_browser_tracking(self) -> list[str]:
        return self.cleaned_data["browser_tracking"] or []

    def clean_time_tracking(self) -> list[str]:
        return self.cleaned_data["time_tracking"] or []


class TrackingDataViewForm(forms.Form):
    # Basic Information
    server_timestamp = forms.DateTimeField(
        required=False, widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    http_method = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    ip_address = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    ip_source = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    organization = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    isp = forms.CharField(required=False, widget=forms.TextInput(attrs={"readonly": "readonly"}))

    # Client Information
    os = forms.CharField(required=False, widget=forms.TextInput(attrs={"readonly": "readonly"}))
    browser = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    platform = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    locale = forms.CharField(required=False, widget=forms.TextInput(attrs={"readonly": "readonly"}))
    client_time = forms.DateTimeField(
        required=False, widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    client_timezone = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"readonly": "readonly"})
    )

    # Location Information
    country = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    region = forms.CharField(required=False, widget=forms.TextInput(attrs={"readonly": "readonly"}))
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={"readonly": "readonly"}))
    latitude = forms.FloatField(
        required=False, widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    longitude = forms.FloatField(
        required=False, widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    location_source = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"readonly": "readonly"})
    )

    # JSON Data
    ip_data = forms.JSONField(required=False, widget=forms.HiddenInput())
    user_agent_data = forms.JSONField(required=False, widget=forms.HiddenInput())
    header_data = forms.JSONField(required=False, widget=forms.HiddenInput())
    form_data = forms.JSONField(required=False, widget=forms.HiddenInput())

    class Meta:
        fieldsets = (
            (
                "Basic Information",
                {
                    "fields": (
                        "server_timestamp",
                        "http_method",
                        "ip_address",
                        "ip_source",
                        "organization",
                        "isp",
                    )
                },
            ),
            (
                "Client Information",
                {
                    "fields": (
                        "os",
                        "browser",
                        "platform",
                        "locale",
                        "client_time",
                        "client_timezone",
                    )
                },
            ),
            (
                "Location Information",
                {
                    "fields": (
                        "country",
                        "region",
                        "city",
                        "latitude",
                        "longitude",
                        "location_source",
                    )
                },
            ),
            (
                "JSON Data",
                {
                    "fields": ("ip_data", "user_agent_data", "header_data", "form_data"),
                    "classes": ("collapse",),
                },
            ),
        )


class TaggitSelect2Widget(ModelSelect2TagWidget):
    model = Tag

    def value_from_datadict(self, data: dict, files: dict, name: str) -> list[str]:
        """Create objects for given non-pimary-key values. Return list of all primary keys."""
        values = set(super().value_from_datadict(data, files, name))
        # This may only work for MyModel, if MyModel has title field.
        # You need to implement this method yourself, to ensure proper object creation.
        pks = self.queryset.filter(**{"pk__in": list(values)}).values_list("pk", flat=True)
        pks = set(map(str, pks))
        cleaned_values = list(pks)
        for val in values - pks:
            cleaned_values.append(self.queryset.create(title=val).pk)
        return cleaned_values


class RecipientSubAdminForm(forms.ModelForm[Recipient]):
    class Meta:
        model = Recipient
        fields = "__all__"
        widgets = {"tags": autocomplete.TaggitSelect2(url="tag-autocomplete")}


class TrackingSubAdminForm(forms.ModelForm[Tracking]):
    class Meta:
        model = Tracking
        fields = ("recipient", "campaign")
