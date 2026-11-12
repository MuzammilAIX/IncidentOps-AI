from rest_framework import serializers
from .models import Investigation, InvestigationStep


class InvestigationStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestigationStep
        fields = ["id", "name", "payload", "created_at"]
        read_only_fields = ["id", "created_at"]


class InvestigationSerializer(serializers.ModelSerializer):
    steps = InvestigationStepSerializer(many=True, read_only=True)
    incident_title = serializers.CharField(source="incident.title", read_only=True)
    step_count = serializers.IntegerField(source="steps.count", read_only=True)

    # FIX: JSONField with required=False + default=list prevents null from being
    # sent to a NOT NULL column. Without these, DRF sends None, and Postgres rejects it.
    findings = serializers.JSONField(required=False, default=list)

    class Meta:
        model = Investigation
        fields = [
            "id",
            "incident",
            "incident_title",
            "status",
            "root_cause",
            "confidence",
            "findings",
            "steps",
            "step_count",
            "started_at",
            "finished_at",
        ]
        read_only_fields = ["id", "started_at", "finished_at"]

    def validate_confidence(self, value):
        if value is not None and not (0.0 <= value <= 1.0):
            raise serializers.ValidationError(
                "Confidence must be between 0.0 and 1.0."
            )
        return value

    def validate_findings(self, value):
        """Reject non-list findings and normalize null → []."""
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("findings must be a list.")
        return value

    def create(self, validated_data):
        """Defense-in-depth: force findings to [] if somehow None slips through."""
        if validated_data.get("findings") is None:
            validated_data["findings"] = []
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Same safety net for updates."""
        if validated_data.get("findings") is None:
            validated_data["findings"] = []
        return super().update(instance, validated_data)