from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RunbookViewSet,
    prometheus_webhook,
    grafana_webhook,
    generic_webhook,
    health,
    AnomalyViewSet,
    AlertViewSet,
    LLMCallViewSet,
)

router = DefaultRouter()
router.register(r"anomalies", AnomalyViewSet, basename="anomaly")
router.register(r"alerts", AlertViewSet, basename="alert")
router.register(r"llm-calls", LLMCallViewSet, basename="llm-call")
router.register(r"runbooks", RunbookViewSet, basename="runbook")

urlpatterns = [
    path("health/", health, name="health"),
    path("webhooks/prometheus/", prometheus_webhook, name="webhook-prometheus"),
    path("webhooks/grafana/", grafana_webhook, name="webhook-grafana"),
    path("webhooks/generic/", generic_webhook, name="webhook-generic"),
    path("", include(router.urls)),
]