# urls.py
from rest_framework.routers import DefaultRouter
from .views import ImageReviewView
from .views import PackagesView


# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


router = DefaultRouter()
router.register(r"packages", PackagesView, basename="packages")
router.register(r"images", ImageReviewView, basename="images")


urlpatterns = router.urls
