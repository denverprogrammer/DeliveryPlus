from api.views import AgentTagViewSet
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
# router.register(r'agents', AgentViewSet)
# router.register(r'campaigns', CampaignViewSet)
# router.register(r'tracking-data', TrackingDataViewSet)
router.register(r"tags", AgentTagViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
