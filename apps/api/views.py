from api.serializers import AgentTagSerializer
from django.db.models import Manager
from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from taggit.models import Tag


class AgentTagViewSet(viewsets.ModelViewSet[Tag]):
    queryset: QuerySet[Tag] | Manager[Tag] | None = Tag.objects.all()
    serializer_class = AgentTagSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["name"]
    ordering_fields = ["name"]
