
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    prometheus_webhook, grafana_webhook, generic_webhook,
    AnomalyViewSet, AlertViewSet,
)

router = DefaultRouter()
router.register(r"anomalies", AnomalyViewSet, basename="anomaly")
router.register(r"alerts", AlertViewSet, basename="alert")

urlpatterns = [
    path("webhooks/prometheus/", prometheus_webhook, name="webhook-prometheus"),
    path("webhooks/grafana/", grafana_webhook, name="webhook-grafana"),
    path("webhooks/generic/", generic_webhook, name="webhook-generic"),
    path("", include(router.urls)),
]
