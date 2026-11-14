"""Monitoring views - webhook endpoints + health check + anomaly list."""
from django.core.cache import cache
from django.db import connection
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Anomaly, Alert
from .serializers import AnomalySerializer, AlertSerializer


# ═══════════════════════════════════════════════════════════
# Webhooks (for Prometheus, Grafana, generic alert ingestion)
# ═══════════════════════════════════════════════════════════

@api_view(["POST"])
@permission_classes([AllowAny])
def prometheus_webhook(request):
    from apps.monitoring.watchers.webhook_ingester import WebhookIngester
    count = WebhookIngester.ingest_prometheus(request.data)
    return Response({"ingested": count}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def grafana_webhook(request):
    from apps.monitoring.watchers.webhook_ingester import WebhookIngester
    count = WebhookIngester.ingest_grafana(request.data)
    return Response({"ingested": count}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def generic_webhook(request):
    from apps.monitoring.watchers.webhook_ingester import WebhookIngester
    count = WebhookIngester.ingest_generic(request.data)
    return Response({"ingested": count}, status=status.HTTP_201_CREATED)


# ═══════════════════════════════════════════════════════════
# Health check (for load balancers, uptime monitors, k8s)
# ═══════════════════════════════════════════════════════════

@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """Health check endpoint. Returns 200 if healthy, 503 if any dependency fails."""
    checks = {}
    status_code = 200

    # Database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            checks["database"] = "ok"
    except Exception as e:
        checks["database"] = "error: " + str(e)
        status_code = 503

    # Redis (via Django cache)
    try:
        cache.set("_health_check", "ok", 5)
        if cache.get("_health_check") == "ok":
            checks["cache"] = "ok"
        else:
            checks["cache"] = "error: read mismatch"
            status_code = 503
    except Exception as e:
        checks["cache"] = "error: " + str(e)
        status_code = 503

    return Response(
        {
            "status": "healthy" if status_code == 200 else "unhealthy",
            "checks": checks,
        },
        status=status_code,
    )


# ═══════════════════════════════════════════════════════════
# ViewSets (Anomalies, Alerts)
# ═══════════════════════════════════════════════════════════

class AnomalyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Anomaly.objects.select_related("service", "incident").all()
    serializer_class = AnomalySerializer
    permission_classes = [permissions.IsAuthenticated]


class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Alert.objects.select_related("service").all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
