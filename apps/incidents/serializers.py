from rest_framework import serializers
from .models import Incident


class IncidentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Incident model.
    - Reads and writes all fields needed to create/update incidents.
    - Service is writable by ID (primary key).
    - Adds computed fields for display.
    """
    service_name = serializers.CharField(source="service.name", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)
    age_seconds = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = [
            "id",
            "title",
            "description",
            "severity",
            "status",
            "service",
            "service_name",
            "created_by",
            "created_by_username",
            "created_at",
            "resolved_at",
            "age_seconds",
        ]
        read_only_fields = ["id", "created_at", "resolved_at", "created_by"]

    def get_age_seconds(self, obj):
        """Return how long ago the incident was created, in seconds."""
        from django.utils import timezone
        if not obj.created_at:
            return None
        return int((timezone.now() - obj.created_at).total_seconds())

    def validate_title(self, value):
        """Reject empty or whitespace-only titles."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value) > 255:
            raise serializers.ValidationError("Title must be 255 characters or fewer.")
        return value.strip()

    def validate_severity(self, value):
        """Reject unknown severity values."""
        valid = {choice[0] for choice in Incident.SEVERITY}
        if value not in valid:
            raise serializers.ValidationError(
                f"Invalid severity '{value}'. Choose from: {sorted(valid)}"
            )
        return value

    def create(self, validated_data):
        """Auto-assign created_by to the requesting user if authenticated."""
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data.setdefault("created_by", request.user)
        return super().create(validated_data)