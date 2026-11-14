
from rest_framework import serializers
from .models import Anomaly, Alert, Baseline, WatcherConfig


class AnomalySerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    incident_id = serializers.IntegerField(source="incident.id", read_only=True, allow_null=True)

    class Meta:
        model = Anomaly
        fields = [
            "id", "service", "service_name", "anomaly_type", "severity",
            "score", "details", "incident_id", "created_at",
        ]


class AlertSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = Alert
        fields = ["id", "service", "service_name", "name", "severity", "firing", "payload", "source", "created_at"]


class BaselineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Baseline
        fields = ["id", "service", "metric_name", "mean", "stddev", "sample_count", "updated_at"]


class WatcherConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatcherConfig
        fields = ["id", "watcher_type", "enabled", "interval_seconds", "config", "last_run", "updated_at"]
