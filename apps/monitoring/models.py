from django.db import models


class Alert(models.Model):
    service = models.ForeignKey(
        "services.Service", on_delete=models.CASCADE, related_name="alerts"
    )
    name = models.CharField(max_length=255)
    severity = models.CharField(max_length=16, default="medium")
    firing = models.BooleanField(default=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
