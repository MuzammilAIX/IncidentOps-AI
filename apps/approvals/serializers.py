from rest_framework import serializers
from .models import ApprovalRequest


class ApprovalRequestSerializer(serializers.ModelSerializer):
    investigation_id = serializers.IntegerField(
        source="investigation.id", read_only=True
    )
    incident_title = serializers.CharField(
        source="investigation.incident.title", read_only=True
    )
    decided_by_username = serializers.CharField(
        source="decided_by.username", read_only=True
    )
    proposed_actions = serializers.JSONField(required=False, default=list)

    class Meta:
        model = ApprovalRequest
        fields = [
            "id",
            "investigation",
            "investigation_id",
            "incident_title",
            "proposed_actions",
            "status",
            "decided_by",
            "decided_by_username",
            "decided_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "decided_at", "decided_by"]

    def validate_proposed_actions(self, value):
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("proposed_actions must be a list.")
        return value

    def create(self, validated_data):
        if validated_data.get("proposed_actions") is None:
            validated_data["proposed_actions"] = []
        return super().create(validated_data)

    def update(self, instance, validated_data):
        from django.utils import timezone
        request = self.context.get("request")

        if validated_data.get("proposed_actions") is None:
            validated_data["proposed_actions"] = []

        new_status = validated_data.get("status", instance.status)
        if new_status in ("approved", "rejected") and instance.status == "pending":
            if request and request.user and request.user.is_authenticated:
                validated_data["decided_by"] = request.user
            validated_data["decided_at"] = timezone.now()

        return super().update(instance, validated_data)
