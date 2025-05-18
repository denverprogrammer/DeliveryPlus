from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import AgentTagViewSet


router = DefaultRouter()
# router.register(r'agents', AgentViewSet)
# router.register(r'campaigns', CampaignViewSet)
# router.register(r'tracking-data', TrackingDataViewSet)
router.register(r'tags', AgentTagViewSet) # type: ignore

urlpatterns = [
    path('', include(router.urls)), # type: ignore
] 