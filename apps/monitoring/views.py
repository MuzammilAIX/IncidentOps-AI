"""Monitoring views - webhook endpoints + health check + anomaly list."""
from django.core.cache import cache
from django.db import connection, models
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
    """Generic webhook: creates an Incident + auto-triggers AI investigation."""
    from apps.monitoring.watchers.webhook_ingester import WebhookIngester
    from apps.incidents.services import trigger_investigation
    from apps.incidents.models import Incident

    try:
        result = WebhookIngester.ingest_as_incident(request.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    triggered = False
    task_id = None
    try:
        incident = Incident.objects.get(id=result["incident_id"])
        queue_result = trigger_investigation(incident)
        triggered = queue_result.get("queued", False)
        task_id = queue_result.get("task_id")
    except Exception:
        pass

    return Response({
        "incident_id": result["incident_id"],
        "service": result["service"],
        "investigation_triggered": triggered,
        "task_id": task_id,
    }, status=status.HTTP_201_CREATED)


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

class RunbookViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only API for team runbooks â€” searchable, browsable."""
    from .models import Runbook
    from .serializers import RunbookSerializer
    queryset = Runbook.objects.all()
    serializer_class = RunbookSerializer
    permission_classes = [AllowAny]
    filter_backends = []
    search_fields = ["code", "title", "content", "keywords"]
    filterset_fields = ["category"]
    ordering = ["code"]

    def list(self, request, *args, **kwargs):
        """Support ?search=... and ?category=..."""
        qs = self.get_queryset()
        search = request.query_params.get("search", "").strip().lower()
        category = request.query_params.get("category", "").strip()
        if search:
            qs = qs.filter(
                models.Q(title__icontains=search) |
                models.Q(content__icontains=search) |
                models.Q(code__icontains=search) |
                models.Q(keywords__icontains=search)
            )
        if category:
            qs = qs.filter(category=category)
        serializer = self.get_serializer(qs, many=True)
        return Response({"count": qs.count(), "results": serializer.data})
