from django.db import models
from django.conf import settings


class Incident(models.Model):
    SEVERITY = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]
    STATUS = [
        ("open", "Open"),
        ("investigating", "Investigating"),
        ("resolved", "Resolved"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=16, choices=SEVERITY, default="medium")
    status = models.CharField(max_length=16, choices=STATUS, default="open")
    service = models.ForeignKey(
        "services.Service", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"[{self.severity}] {self.title}"
