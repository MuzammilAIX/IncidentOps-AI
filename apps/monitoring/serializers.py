
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


class LLMCallSerializer(serializers.ModelSerializer):
    estimated_cost_usd = serializers.FloatField(read_only=True)

    class Meta:
        from .models import LLMCall
        model = LLMCall
        fields = [
            "id", "investigation", "agent_name", "model",
            "prompt_tokens", "completion_tokens", "total_tokens",
            "latency_ms", "success", "error_message",
            "estimated_cost_usd", "created_at",
        ]
