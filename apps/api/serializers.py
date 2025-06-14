from rest_framework.serializers import ModelSerializer
from tracking.models import AgentTag


class AgentTagSerializer(ModelSerializer[AgentTag]):
    class Meta:
        model = AgentTag
        fields = ("id", "name")


# from tracking.models import Agent, Campaign, TrackingData, AgentTag


# class AgentSerializer(serializers.ModelSerializer):
#     tags = AgentTagSerializer(many=True, read_only=True)

#     class Meta:
#         model = Agent
#         fields = [
#             'id', 'first_name', 'last_name', 'email',
#             'phone_number', 'token', 'status', 'tags'
#         ]

# class CampaignSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Campaign
#         fields = '__all__'

# class TrackingDataSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TrackingData
#         fields = '__all__'
