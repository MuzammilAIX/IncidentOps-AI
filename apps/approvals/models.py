from django.db import models
from django.conf import settings


class ApprovalRequest(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    investigation = models.ForeignKey(
        "investigations.Investigation", on_delete=models.CASCADE, related_name="approvals"
    )
    proposed_actions = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=16, choices=STATUS, default="pending")
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
