from django.contrib import admin
from .models import Investigation, InvestigationStep


class InvestigationStepInline(admin.TabularInline):
    model = InvestigationStep
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Investigation)
class InvestigationAdmin(admin.ModelAdmin):
    list_display = ("id", "incident", "status", "root_cause", "confidence", "started_at")
    list_filter = ("status",)
    inlines = [InvestigationStepInline]


@admin.register(InvestigationStep)
class InvestigationStepAdmin(admin.ModelAdmin):
    list_display = ("id", "investigation", "name", "created_at")
