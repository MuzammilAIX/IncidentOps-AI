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

class Runbook(models.Model):
    """Team runbook — trusted troubleshooting instructions the agent can consult."""
    CATEGORIES = [
        ("network", "Network"),
        ("database", "Database"),
        ("container", "Container / Docker"),
        ("deployment", "Deployment / Rollback"),
        ("resource", "CPU / Memory"),
        ("auth", "Authentication"),
        ("other", "Other"),
    ]

    code = models.CharField(max_length=32, unique=True)       # e.g., "RB-102"
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=16, choices=CATEGORIES, default="other")
    content = models.TextField()
    keywords = models.JSONField(default=list, blank=True)     # ["payment", "500", "migration"]
    service_hint = models.CharField(max_length=128, blank=True)  # optional: applies to specific service
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.title}"


class LLMCall(models.Model):
    """One LLM API call — observability, cost tracking, latency analysis."""
    AGENT_CHOICES = [
        ("triage", "Triage Agent"),
        ("diagnosis", "Diagnosis Agent"),
        ("remediation", "Remediation Agent"),
        ("verifier", "Verifier Agent"),
        ("other", "Other"),
    ]

    investigation = models.ForeignKey(
        "investigations.Investigation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="llm_calls",
    )
    agent_name = models.CharField(max_length=32, choices=AGENT_CHOICES, default="other")
    model = models.CharField(max_length=64)
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    latency_ms = models.IntegerField(default=0)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["investigation", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.agent_name} ({self.total_tokens} tokens, {self.latency_ms}ms)"

    @property
    def estimated_cost_usd(self):
        prompt_cost = (self.prompt_tokens / 1_000_000) * 0.15
        completion_cost = (self.completion_tokens / 1_000_000) * 0.60
        return round(prompt_cost + completion_cost, 6)
