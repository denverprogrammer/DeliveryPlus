# from common.api_clients import TwilioApiClient
# from common.api_clients import TwilioLookupResponse
from typing import Optional
from common.enums import CampaignDataType
from dal import autocomplete

# from config import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import Http404
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from taggit.models import Tag
from tracking.forms import TrackingDataViewForm
from tracking.models import AbstractRequestData
from tracking.models import ImageRequestData
from tracking.models import TrackingRequestData


@staff_member_required
def tracking_data_modal(request: HttpRequest, campaign_type: str, pk: int) -> TemplateResponse:
    """View for displaying tracking data in a read-only format."""

    obj: Optional[AbstractRequestData] = None

    if campaign_type == CampaignDataType.PACKAGES.value:
        obj = get_object_or_404(TrackingRequestData, pk=pk)
    elif campaign_type == CampaignDataType.IMAGES.value:
        obj = get_object_or_404(ImageRequestData, pk=pk)
    else:
        raise Http404("Invalid campaign type")

    form = TrackingDataViewForm(
        initial={
            "server_timestamp": obj.server_timestamp,
            "http_method": obj.http_method,
            "ip_address": obj.ip_address,
            "ip_source": obj.ip_source,
            "organization": obj.ip_data.getSelectedOrganization() if obj.ip_data else None,
            "isp": obj.ip_data.getSelectedISP() if obj.ip_data else None,
            "os": obj.os,
            "browser": obj.browser,
            "platform": obj.platform,
            "locale": obj.locale,
            "client_time": obj.client_time,
            "client_timezone": obj.client_timezone,
            "country": obj.ip_data.getSelectedCountryName() if obj.ip_data else None,
            "region": obj.ip_data.getSelectedRegion() if obj.ip_data else None,
            "city": obj.ip_data.getSelectedCity() if obj.ip_data else None,
            "latitude": obj.latitude,
            "longitude": obj.longitude,
            "location_source": obj.location_source,
            "ip_data": obj.ip_data.model_dump() if obj.ip_data else None,
            "user_agent_data": obj.user_agent_data.model_dump() if obj.user_agent_data else None,
            "header_data": obj.header_data.model_dump() if obj.header_data else None,
            "form_data": obj.form_data,
        }
    )

    context = {
        "form": form,
        "title": f"Request Data for {obj.tracking}",
        "json_fields": ["ip_data", "user_agent_data", "header_data", "form_data"],
        "warnings": obj.all_warnings,
    }

    return TemplateResponse(request, "tracking/tracking_data_modal.html", context)


class TagAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self) -> QuerySet[Tag]:
        # Get company_id from URL parameters
        company_id = self.kwargs.get("company_id")

        # Filter by company if company_id is provided
        qs: QuerySet[Tag] = Tag.objects.all()

        if company_id:
            qs = qs.filter(company_id=company_id)

        # Don't forget to filter out results if a query is provided
        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


# class TagAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
#     def get_queryset(self) -> QuerySet[CompanyTag]:
