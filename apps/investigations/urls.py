from rest_framework.routers import DefaultRouter
from .views import InvestigationViewSet, InvestigationStepViewSet

router = DefaultRouter()
router.register(r"steps", InvestigationStepViewSet, basename="investigation-step")
router.register(r"", InvestigationViewSet, basename="investigation")

urlpatterns = router.urls