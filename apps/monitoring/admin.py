from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "service", "severity", "firing", "created_at")
    list_filter = ("severity", "firing")
    search_fields = ("name",)
