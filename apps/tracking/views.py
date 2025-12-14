# from common.api_clients import TwilioApiClient
# from common.api_clients import TwilioLookupResponse
from dal import autocomplete

# from config import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from taggit.models import Tag
from tracking.forms import TrackingDataViewForm
from tracking.models import TrackingRequestData


@staff_member_required
def tracking_data_modal(request: HttpRequest, pk: int) -> TemplateResponse:
    """View for displaying tracking data in a read-only format."""
    tracking_data = get_object_or_404(TrackingRequestData, pk=pk)

    form = TrackingDataViewForm(
        initial={
            "server_timestamp": tracking_data.server_timestamp,
            "http_method": tracking_data.http_method,
            "ip_address": tracking_data.ip_address,
            "ip_source": tracking_data.ip_source,
            "organization": (
                tracking_data.ip_data.getSelectedOrganization() if tracking_data.ip_data else None
            ),
            "isp": tracking_data.ip_data.getSelectedISP() if tracking_data.ip_data else None,
            "os": tracking_data.os,
            "browser": tracking_data.browser,
            "platform": tracking_data.platform,
            "locale": tracking_data.locale,
            "client_time": tracking_data.client_time,
            "client_timezone": tracking_data.client_timezone,
            "country": (
                tracking_data.ip_data.getSelectedCountryName() if tracking_data.ip_data else None
            ),
            "region": tracking_data.ip_data.getSelectedRegion() if tracking_data.ip_data else None,
            "city": tracking_data.ip_data.getSelectedCity() if tracking_data.ip_data else None,
            "latitude": tracking_data.latitude,
            "longitude": tracking_data.longitude,
            "location_source": tracking_data.location_source,
            "ip_data": tracking_data.ip_data.model_dump() if tracking_data.ip_data else None,
            "user_agent_data": (
                tracking_data.user_agent_data.model_dump()
                if tracking_data.user_agent_data
                else None
            ),
            "header_data": (
                tracking_data.header_data.model_dump() if tracking_data.header_data else None
            ),
            "form_data": tracking_data.form_data,
        }
    )

    context = {
        "form": form,
        "title": f"Tracking Data for {tracking_data.tracking}",
        "json_fields": ["ip_data", "user_agent_data", "header_data", "form_data"],
        "warnings": tracking_data.all_warnings,
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
