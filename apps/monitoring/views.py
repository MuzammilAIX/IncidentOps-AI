
"""Monitoring views — webhook endpoints + anomaly list."""
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Anomaly, Alert
from .serializers import AnomalySerializer, AlertSerializer


@api_view(["POST"])
@permission_classes([permissions.AllowAny])   # Webhooks must be open (or use shared secret)
def prometheus_webhook(request):
    from apps.monitoring.watchers.webhook_ingester import WebhookIngester
    count = WebhookIngester.ingest_prometheus(request.data)
    return Response({"ingested": count}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def grafana_webhook(request):
    from apps.monitoring.watchers.webhook_ingester import WebhookIngester
    count = WebhookIngester.ingest_grafana(request.data)
    return Response({"ingested": count}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def generic_webhook(request):
    from apps.monitoring.watchers.webhook_ingester import WebhookIngester
    count = WebhookIngester.ingest_generic(request.data)
    return Response({"ingested": count}, status=status.HTTP_201_CREATED)


class AnomalyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Anomaly.objects.select_related("service", "incident").all()
    serializer_class = AnomalySerializer
    permission_classes = [permissions.IsAuthenticated]


class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Alert.objects.select_related("service").all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
