from django.contrib import admin
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "endpoint", "created_at")
    search_fields = ("name", "kind")
    list_filter = ("kind",)
