from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "actor", "action", "target_type", "target_id", "created_at")
    list_filter = ("action", "target_type")
    search_fields = ("action", "target_type", "target_id")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
