"""Monitoring views - webhook endpoints + health check + anomaly list."""
from django.core.cache import cache
from django.db import connection
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Anomaly, Alert, LLMCall
from .serializers import AnomalySerializer, AlertSerializer, LLMCallSerializer


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


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """Health check endpoint."""
    db_ok = False
    cache_ok = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_ok = True
    except Exception:
        pass
    try:
        cache.set("health_check", "ok", 5)
        cache_ok = cache.get("health_check") == "ok"
    except Exception:
        pass
    return Response({
        "status": "healthy" if (db_ok and cache_ok) else "degraded",
        "checks": {"database": "ok" if db_ok else "fail", "cache": "ok" if cache_ok else "fail"},
    })


class AnomalyViewSet(viewsets.ModelViewSet):
    queryset = Anomaly.objects.select_related("service", "incident").all()
    serializer_class = AnomalySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["service", "severity", "anomaly_type"]
    ordering = ["-created_at"]


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related("service").all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["service", "severity", "firing"]
    ordering = ["-created_at"]


class LLMCallViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only LLM call log for observability."""
    queryset = LLMCall.objects.select_related("investigation").all()
    serializer_class = LLMCallSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["investigation", "agent_name", "success"]
    ordering = ["-created_at"]