# urls.py
from rest_framework.routers import DefaultRouter
from .views import PackagesView


# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


router = DefaultRouter()
router.register(r"packages", PackagesView, basename="packages")


urlpatterns = router.urls
