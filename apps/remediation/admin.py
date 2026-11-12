from django.contrib import admin
from .models import RemediationExecution


@admin.register(RemediationExecution)
class RemediationExecutionAdmin(admin.ModelAdmin):
    list_display = ("id", "approval", "status", "started_at", "finished_at")
    list_filter = ("status",)
    readonly_fields = ("started_at", "finished_at")
