from django.contrib import admin
from .models import ApprovalRequest


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "investigation", "status", "decided_by", "created_at")
    list_filter = ("status",)
    readonly_fields = ("created_at", "decided_at")
