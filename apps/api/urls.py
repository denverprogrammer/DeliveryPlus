# urls.py
from rest_framework.routers import DefaultRouter
from .management_views import CampaignViewSet
from .management_views import CompanyViewSet
from .management_views import RecipientViewSet
from .management_views import RequestDataViewSet
from .management_views import SignupViewSet
from .management_views import TrackingViewSet
from .management_views import UserViewSet
from .views import ImageReviewView
from .views import PackagesView


# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


router = DefaultRouter()
router.register(r"packages", PackagesView, basename="packages")
router.register(r"images", ImageReviewView, basename="images")
# Management API endpoints
router.register(r"management/signup", SignupViewSet, basename="signup")
router.register(r"management/users", UserViewSet, basename="users")
router.register(r"management/companies", CompanyViewSet, basename="companies")
router.register(r"management/recipients", RecipientViewSet, basename="recipients")
router.register(r"management/campaigns", CampaignViewSet, basename="campaigns")
router.register(r"management/tracking", TrackingViewSet, basename="tracking")
router.register(r"management/request-data", RequestDataViewSet, basename="request-data")


urlpatterns = router.urls
