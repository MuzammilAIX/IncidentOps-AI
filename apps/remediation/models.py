from django.db import models


class RemediationExecution(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("done", "Done"),
        ("failed", "Failed"),
    ]

    approval = models.OneToOneField(
        "approvals.ApprovalRequest", on_delete=models.CASCADE, related_name="execution"
    )
    status = models.CharField(max_length=16, choices=STATUS, default="pending")
    log = models.JSONField(default=list, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
