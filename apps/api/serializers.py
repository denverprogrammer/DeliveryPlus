from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from taggit.models import Tag
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

    class Meta:
        model = Recipient
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "status",
            "tags",
        ]


class TokenSerializer(ModelSerializer[Token]):
    class Meta:
        model = Token
        fields = [
            "id",
            "value",
            "status",
            "created_on",
            "deleted_on",
        ]


class TrackingSerializer(ModelSerializer[Tracking]):
    tokens = TokenSerializer(many=True, read_only=True)
    token_values = serializers.SerializerMethodField()

    class Meta:
        model = Tracking
        fields = [
            "id",
            "tokens",
            "token_values",
            "campaign",
            "recipient",
            "company",
        ]

    def get_token_values(self, obj: Tracking) -> list[str]:
        """Return list of token values."""
        return [token.value for token in obj.tokens.all()]


class CampaignSerializer(ModelSerializer[Campaign]):
    class Meta:
        model = Campaign
        fields = "__all__"


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
    image = serializers.ImageField()
