from typing import Any
from mgmt.models import Company
from mgmt.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from taggit.models import Tag
from tracking.models import AbstractRequestData
from tracking.models import Campaign
from tracking.models import Recipient
from tracking.models import Token
from tracking.models import Tracking
from tracking.models import TrackingData


class RecipientTagSerializer(ModelSerializer[Tag]):
    class Meta:
        model = Tag
        fields = ("id", "name")


class RecipientSerializer(ModelSerializer[Recipient]):
    tags = RecipientTagSerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Recipient
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone_number",
            "status",
            "tags",
        ]

    def get_full_name(self, obj: Recipient) -> str:
        """Return recipient full name."""
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip()


class TokenSerializer(ModelSerializer[Token]):
    used = serializers.SerializerMethodField()

    class Meta:
        model = Token
        fields = [
            "id",
            "value",
            "status",
            "created_on",
            "last_used",
            "deleted_on",
            "used",
        ]

    def get_used(self, obj: Token) -> int | str:
        """Return count of requests for this token's tracking."""
        try:
            if obj.tracking:
                return obj.tracking.count_requests or 0
        except AttributeError:
            pass
        return 0


class TrackingRequestDataSerializer(ModelSerializer):
    """Serializer for TrackingRequestData."""

    organization = serializers.SerializerMethodField()
    isp = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    _ip_data = serializers.SerializerMethodField()
    _user_agent_data = serializers.SerializerMethodField()
    _header_data = serializers.SerializerMethodField()
    _form_data = serializers.SerializerMethodField()
    warnings = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        from tracking.models import TrackingRequestData

        model = TrackingRequestData
        fields = [
            "id",
            "data_type",
            "http_method",
            "server_timestamp",
            "ip_address",
            "ip_source",
            "organization",
            "isp",
            "os",
            "browser",
            "platform",
            "locale",
            "client_time",
            "client_timezone",
            "country",
            "region",
            "city",
            "latitude",
            "longitude",
            "location_source",
            "_ip_data",
            "_user_agent_data",
            "_header_data",
            "_form_data",
            "warnings",
            "image_url",
        ]
        read_only_fields = fields

    def get_organization(self, obj: AbstractRequestData) -> str | None:
        """Get organization from IP data."""
        if obj.ip_data:
            return obj.ip_data.getSelectedOrganization()
        return None

    def get_isp(self, obj: AbstractRequestData) -> str | None:
        """Get ISP from IP data."""
        if obj.ip_data:
            return obj.ip_data.getSelectedISP()
        return None

    def get_country(self, obj: AbstractRequestData) -> str | None:
        """Get country from IP data."""
        if obj.ip_data:
            return obj.ip_data.getSelectedCountryName()
        return None

    def get_region(self, obj: AbstractRequestData) -> str | None:
        """Get region from IP data."""
        if obj.ip_data:
            return obj.ip_data.getSelectedRegion()
        return None

    def get_city(self, obj: AbstractRequestData) -> str | None:
        """Get city from IP data."""
        if obj.ip_data:
            return obj.ip_data.getSelectedCity()
        return None

    def get__ip_data(self, obj: AbstractRequestData) -> dict[str, Any] | None:
        """Get IP data as dict."""
        if obj.ip_data:
            return obj.ip_data.model_dump()
        return None

    def get__user_agent_data(self, obj: AbstractRequestData) -> dict[str, Any] | None:
        """Get user agent data as dict."""
        if obj.user_agent_data:
            return obj.user_agent_data.model_dump()
        return None

    def get__header_data(self, obj: AbstractRequestData) -> dict[str, Any] | None:
        """Get header data as dict."""
        if obj.header_data:
            return obj.header_data.model_dump()
        return None

    def get__form_data(self, obj: AbstractRequestData) -> dict[str, Any] | None:
        """Get form data as dict."""
        return obj.form_data

    def get_warnings(self, obj: AbstractRequestData) -> dict[str, Any]:
        """Get all warnings."""
        return obj.all_warnings

    def get_image_url(self, obj: AbstractRequestData) -> str | None:
        """Get image URL if available."""
        return None


class ImageRequestDataSerializer(ModelSerializer):
    """Serializer for ImageRequestData."""

    organization = serializers.SerializerMethodField()
    isp = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    _ip_data = serializers.SerializerMethodField()
    _user_agent_data = serializers.SerializerMethodField()
    _header_data = serializers.SerializerMethodField()
    _form_data = serializers.SerializerMethodField()
    warnings = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        from tracking.models import ImageRequestData

        model = ImageRequestData
        fields = [
            "id",
            "data_type",
            "http_method",
            "server_timestamp",
            "ip_address",
            "ip_source",
            "organization",
            "isp",
            "os",
            "browser",
            "platform",
            "locale",
            "client_time",
            "client_timezone",
            "country",
            "region",
            "city",
            "latitude",
            "longitude",
            "location_source",
            "_ip_data",
            "_user_agent_data",
            "_header_data",
            "_form_data",
            "warnings",
            "image_url",
            "image",
            "altitude",
            "make",
            "model",
            "software",
            "width",
            "height",
            "orientation",
            "datetime_original",
            "datetime_digitized",
            "exposure_time",
            "f_number",
            "iso_speed",
            "focal_length",
            "flash",
            "raw_exif_data",
        ]
        read_only_fields = fields

    def get_organization(self, obj: AbstractRequestData) -> str | None:
        """Get organization from IP data."""
        if obj.ip_data:
            return obj.ip_data.getSelectedOrganization()
        return None

    def get_isp(self, obj: AbstractRequestData) -> str | None:
        """Get ISP from IP data."""
        if obj.ip_data:
            return obj.ip_data.getSelectedISP()
        return None

    def get_country(self, obj: AbstractRequestData) -> str | None:
        """Get country from IP data."""
        if obj.ip_data:
            return obj.ip_data.getSelectedCountryName()
        return None

    def get_region(self, obj: AbstractRequestData) -> str | None:
        """Get region from IP data."""
        if obj.ip_data:
            return obj.ip_data.getSelectedRegion()
        return None

    def get_city(self, obj: AbstractRequestData) -> str | None:
        """Get city from IP data."""
        if obj.ip_data:
            return obj.ip_data.getSelectedCity()
        return None

    def get__ip_data(self, obj: AbstractRequestData) -> dict[str, Any] | None:
        """Get IP data as dict."""
        if obj.ip_data:
            return obj.ip_data.model_dump()
        return None

    def get__user_agent_data(self, obj: AbstractRequestData) -> dict[str, Any] | None:
        """Get user agent data as dict."""
        if obj.user_agent_data:
            return obj.user_agent_data.model_dump()
        return None

    def get__header_data(self, obj: AbstractRequestData) -> dict[str, Any] | None:
        """Get header data as dict."""
        if obj.header_data:
            return obj.header_data.model_dump()
        return None

    def get__form_data(self, obj: AbstractRequestData) -> dict[str, Any] | None:
        """Get form data as dict."""
        return obj.form_data

    def get_warnings(self, obj: AbstractRequestData) -> dict[str, Any]:
        """Get all warnings."""
        return obj.all_warnings

    def get_image_url(self, obj: AbstractRequestData) -> str | None:
        """Get image URL if available."""
        from django.conf import settings

        if hasattr(obj, "image") and obj.image:
            request = self.context.get("request")
            if request:
                return str(request.build_absolute_uri(obj.image.url))
            return f"{settings.MEDIA_URL}{obj.image.url.lstrip('/')}"
        return None


class CampaignSerializer(ModelSerializer[Campaign]):
    class Meta:
        model = Campaign
        fields = "__all__"


class TrackingListSerializer(ModelSerializer[Tracking]):
    """Serializer for tracking list view - includes nested campaign and recipient, excludes request_data, tokens, token_values, campaign_name, and recipient_name."""

    campaign = CampaignSerializer(read_only=True)
    recipient = RecipientSerializer(read_only=True, allow_null=True)
    count_requests = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tracking
        fields = [
            "id",
            "campaign",
            "recipient",
            "company",
            "count_requests",
        ]
        read_only_fields = ["id", "company", "count_requests"]


class TrackingDetailSerializer(ModelSerializer[Tracking]):
    """Serializer for tracking detail view - includes request_data and tokens."""

    tokens = TokenSerializer(many=True, read_only=True)
    token_values = serializers.SerializerMethodField()
    campaign = CampaignSerializer(read_only=True)
    recipient = RecipientSerializer(read_only=True, allow_null=True)
    count_requests = serializers.IntegerField(read_only=True)
    request_data = serializers.SerializerMethodField()

    class Meta:
        model = Tracking
        fields = [
            "id",
            "tokens",
            "token_values",
            "campaign",
            "recipient",
            "company",
            "count_requests",
            "request_data",
        ]
        read_only_fields = ["id", "company", "count_requests"]

    def get_token_values(self, obj: Tracking) -> list[str]:
        """Return list of token values."""
        return [token.value for token in obj.tokens.all()]

    def get_request_data(self, obj: Tracking) -> list[dict[str, Any]]:
        """Return request data based on campaign type."""
        from common.enums import CampaignDataType
        from tracking.models import ImageRequestData
        from tracking.models import TrackingRequestData

        if not obj.campaign:
            return []

        if obj.campaign.campaign_type == CampaignDataType.PACKAGES.value:
            # Get TrackingRequestData
            tracking_data = TrackingRequestData.objects.filter(tracking=obj).order_by(
                "-server_timestamp"
            )[:20]
            tracking_serializer: Any = TrackingRequestDataSerializer(tracking_data, many=True)
            return list(tracking_serializer.data)
        elif obj.campaign.campaign_type == CampaignDataType.IMAGES.value:
            # Get ImageRequestData
            image_data = ImageRequestData.objects.filter(tracking=obj).order_by(
                "-server_timestamp"
            )[:20]
            image_serializer: Any = ImageRequestDataSerializer(image_data, many=True)
            return list(image_serializer.data)

        return []


# Keep TrackingSerializer as alias for backward compatibility, but use TrackingListSerializer for list
TrackingSerializer = TrackingListSerializer


class TrackingDataSerializer(ModelSerializer[TrackingData]):
    class Meta:
        model = TrackingData
        fields = "__all__"


class RequestSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)
    method = serializers.CharField(max_length=20)


class NotificationSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)
    method = serializers.CharField(max_length=20)
    phone = serializers.CharField(max_length=20)


class AddressSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)
    method = serializers.CharField(max_length=20)
    line1 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    line2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    city = serializers.CharField(max_length=255, required=False, allow_blank=True)
    provinceOrState = serializers.CharField(max_length=50, required=False, allow_blank=True)
    postalOrZip = serializers.CharField(max_length=20, required=False, allow_blank=True)
    country = serializers.CharField(max_length=2, required=False, allow_blank=True)
    recipient = serializers.CharField(max_length=255, required=False, allow_blank=True)


class ImageUploadSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)
    method = serializers.CharField(max_length=20)
    image = serializers.ImageField()


class UserSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    current_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "company",
            "password",
            "current_password",
        ]
        read_only_fields = ["id", "company"]


class UserCreateSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_active",
            "is_staff",
            "company",
        ]
        read_only_fields = ["id", "company"]


class CompanySerializer(ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "street_address",
            "city",
            "state",
            "zip_code",
            "country",
            "phone_number",
        ]
