from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from tracking.models import AgentTag
from api.serializers import  AgentTagSerializer

class AgentTagViewSet(viewsets.ModelViewSet):
    queryset = AgentTag.objects.all()
    serializer_class = AgentTagSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name']
    ordering_fields = ['name'] 