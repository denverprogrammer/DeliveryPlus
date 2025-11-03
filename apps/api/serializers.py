from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from taggit.models import Tag
from tracking.models import Agent
from tracking.models import Campaign
from tracking.models import TrackingData


class AgentTagSerializer(ModelSerializer[Tag]):
    class Meta:
        model = Tag
        fields = ("id", "name")


class AgentSerializer(ModelSerializer[Agent]):
    tags = AgentTagSerializer(many=True, read_only=True)

    class Meta:
        model = Agent
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "token",
            "status",
            "tags",
        ]


class CampaignSerializer(ModelSerializer[Campaign]):
    class Meta:
        model = Campaign
        fields = "__all__"


class TrackingDataSerializer(ModelSerializer[TrackingData]):
    class Meta:
        model = TrackingData
        fields = "__all__"


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)
    method = serializers.CharField(max_length=20)
