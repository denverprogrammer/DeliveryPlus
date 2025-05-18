from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from tracking.models import AgentTag
from api.serializers import AgentTagSerializer
from django.db.models import QuerySet, Manager


class AgentTagViewSet(viewsets.ModelViewSet[AgentTag]):
    queryset: QuerySet[AgentTag] | Manager[AgentTag] | None = AgentTag.objects.all()
    serializer_class = AgentTagSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["name"]
    ordering_fields = ["name"]
