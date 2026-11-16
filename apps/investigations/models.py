from django.conf import settings
from django.db import models


class Investigation(models.Model):
    STATUS = [
        ("running", "Running"),
        ("done", "Done"),
        ("failed", "Failed"),
    ]

    incident = models.ForeignKey(
        "incidents.Incident", on_delete=models.CASCADE, related_name="investigations"
    )
    status = models.CharField(max_length=16, choices=STATUS, default="running")
    root_cause = models.TextField(blank=True)
    confidence = models.FloatField(default=0.0)
    findings = models.JSONField(default=list, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Investigation<{self.incident_id}>"


class InvestigationStep(models.Model):
    investigation = models.ForeignKey(
        Investigation, on_delete=models.CASCADE, related_name="steps"
    )
    name = models.CharField(max_length=64)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Feedback(models.Model):
    """User feedback on a diagnosis — used to iteratively improve the agent."""
    VERDICTS = [
        ("correct", "Correct diagnosis"),
        ("partial", "Partially correct"),
        ("wrong", "Wrong diagnosis"),
        ("unclear", "Unclear"),
    ]

    investigation = models.ForeignKey(
        Investigation, on_delete=models.CASCADE, related_name="feedback_entries"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    verdict = models.CharField(max_length=16, choices=VERDICTS)
    comment = models.TextField(blank=True)
    actual_root_cause = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Feedback<{self.investigation_id}>: {self.verdict}"
