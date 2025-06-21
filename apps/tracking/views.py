from typing import Optional

# from common.api_clients import TwilioApiClient
# from common.api_clients import TwilioLookupResponse
from common.api_types import HeaderData
from common.api_types import IpData
from common.api_types import LocaleData
from common.api_types import LocationData
from common.api_types import TimeData
from common.api_types import UserAgentData
from common.functions import get_ip_data
from common.functions import get_locale_data
from common.functions import get_location_data
from common.functions import get_time_data
from common.functions import get_user_agent_data
from dal import autocomplete

# from config import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from taggit.models import Tag
from tracking.forms import TrackingDataViewForm
from tracking.models import Agent
from tracking.models import TrackingData


@csrf_exempt
def track_view(request: HttpRequest, token: Optional[str] = None) -> HttpResponse:
    if token and request.method == "POST":
        # Add breakpoint for debugging
        agent = get_object_or_404(Agent, token=token)
        header_data: HeaderData = getattr(request, "header_data ")
        http_method: str = request.POST.get("http_method", request.method)

        # Get IP data
        ip_data: IpData = get_ip_data(request, header_data)
        print(f"ip data: {ip_data}")

        # Get user agent data
        user_agent_data: UserAgentData = get_user_agent_data(request, header_data)

        # Get locale data
        locale_data: LocaleData = get_locale_data(request, header_data)

        # Get time data
        time_data: TimeData = get_time_data(header_data, ip_data)

        # Get location data
        location_data: LocationData = get_location_data(header_data, ip_data)

        # Create tracking data
        TrackingData.objects.create(
            agent=agent,
            http_method=http_method,
            ip_address=ip_data.getSelectedAddress(),
            ip_source=ip_data.source,
            os=user_agent_data.get_os_name(),
            browser=user_agent_data.get_browser_name(),
            platform=user_agent_data.get_platform_type(),
            locale=locale_data.selected,
            client_time=time_data.info,
            client_timezone=time_data.getTimezone(),
            latitude=location_data.getLatitude(),
            longitude=location_data.getLongitude(),
            location_source=location_data.source,
            _ip_data=ip_data.model_dump(),
            _user_agent_data=user_agent_data.model_dump(),
            _header_data=header_data.model_dump(),
            _form_data=request.POST,
        )

        return JsonResponse(
            {
                "status": "success",
                "message": "✅ Your package was picked up by a local carrier. It may take a few hours to arrive at the sorting facility.",
            }
        )

    # For GET request: serve Django template
    return render(request, "tracking/track.html", {})


@csrf_exempt
def redirect_package_view(request: HttpRequest, token: Optional[str] = None) -> HttpResponse:
    if token and request.method == "POST":
        agent = get_object_or_404(Agent, token=token)
        header_data: HeaderData = getattr(request, "header_data ")
        http_method = request.POST.get("http_method", request.method)
        # notifications = request.POST.get("notifications")

        # Get IP data
        ip_data: IpData = get_ip_data(request, header_data)
        print(f"ip data: {ip_data}")

        # Get user agent data
        user_agent_data: UserAgentData = get_user_agent_data(request, header_data)

        # Get locale data
        locale_data: LocaleData = get_locale_data(request, header_data)

        # Get time data
        time_data: TimeData = get_time_data(header_data, ip_data)

        # Get location data
        location_data: LocationData = get_location_data(header_data, ip_data)

        # Handle notifications if provided
        # phone_data: Optional[TwilioLookupResponse] = None
        # if notifications:
        #     twilio_client = TwilioApiClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        #     phone_data = twilio_client.get_data(notifications)

        # Create tracking data
        TrackingData.objects.create(
            agent=agent,
            http_method=http_method,
            ip_address=ip_data.getSelectedAddress(),
            ip_source=ip_data.source,
            os=user_agent_data.get_os_name(),
            browser=user_agent_data.get_browser_name(),
            platform=user_agent_data.get_platform_type(),
            locale=locale_data.selected,
            client_time=time_data.info,
            client_timezone=time_data.getTimezone(),
            latitude=location_data.getLatitude(),
            longitude=location_data.getLongitude(),
            location_source=location_data.source,
            _ip_data=ip_data.model_dump(),
            _user_agent_data=user_agent_data.model_dump(),
            _header_data=header_data.model_dump(),
            _form_data=request.POST,
            # _phone_data=phone_data.model_dump() if phone_data else None,
        )

        return JsonResponse(
            {
                "status": "success",
                "message": "✅ A request was sent to redirect your package. Please check your phone for updates we have sent you.",
            }
        )

    return render(request, "tracking/redirect.html", {})


@staff_member_required
def tracking_data_modal(request: HttpRequest, pk: int) -> TemplateResponse:
    """View for displaying tracking data in a read-only format."""
    tracking_data = get_object_or_404(TrackingData, pk=pk)

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
        "title": f"Tracking Data for {tracking_data.agent}",
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
