from django.db import models
from django.conf import settings


class Alert(models.Model):
    service = models.ForeignKey(
        "services.Service", on_delete=models.CASCADE, related_name="alerts"
    )
    name = models.CharField(max_length=255)
    severity = models.CharField(max_length=16, default="medium")
    firing = models.BooleanField(default=True)
    payload = models.JSONField(default=dict, blank=True)
    source = models.CharField(max_length=32, default="manual")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} [{self.severity}]"


class WatcherConfig(models.Model):
    """Configuration for each watcher type."""
    WATCHER_TYPES = [
        ("log", "Log Scanner"),
        ("metric", "Metric Poller"),
        ("health", "Health Checker"),
    ]
    watcher_type = models.CharField(max_length=16, choices=WATCHER_TYPES)
    enabled = models.BooleanField(default=True)
    interval_seconds = models.IntegerField(default=60)
    config = models.JSONField(default=dict, blank=True)
    last_run = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("watcher_type",)

    def __str__(self):
        return f"{self.watcher_type} (enabled={self.enabled})"


class Baseline(models.Model):
    """Rolling baseline for a service metric."""
    service = models.ForeignKey(
        "services.Service", on_delete=models.CASCADE, related_name="baselines"
    )
    metric_name = models.CharField(max_length=128)
    mean = models.FloatField(default=0.0)
    stddev = models.FloatField(default=0.0)
    sample_count = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("service", "metric_name")

    def __str__(self):
        return f"{self.service.name}:{self.metric_name}"


class Anomaly(models.Model):
    """Detected anomaly — becomes an Incident when severe enough."""
    SEVERITY = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    service = models.ForeignKey(
        "services.Service", on_delete=models.CASCADE, related_name="anomalies"
    )
    anomaly_type = models.CharField(max_length=64)
    severity = models.CharField(max_length=16, choices=SEVERITY, default="medium")
    score = models.FloatField(default=0.0)
    details = models.JSONField(default=dict, blank=True)
    incident = models.ForeignKey(
        "incidents.Incident",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="anomalies",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.anomaly_type} on {self.service.name}"
