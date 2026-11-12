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
