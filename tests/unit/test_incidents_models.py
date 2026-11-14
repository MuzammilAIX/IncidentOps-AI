"""Unit tests for Incident model."""
import pytest
from datetime import timedelta
from django.utils import timezone

from apps.incidents.models import Incident


@pytest.mark.django_db
class TestIncidentModel:
    def test_create_incident(self, service, user):
        incident = Incident.objects.create(
            title="Test incident",
            description="Test description",
            severity="high",
            status="open",
            service=service,
            created_by=user,
        )
        assert incident.id is not None
        assert incident.title == "Test incident"
        assert incident.severity == "high"
        assert incident.service == service
        assert incident.created_by == user

    def test_str_representation(self, incident):
        assert str(incident) == "[high] API returning 500s"

    def test_severity_choices(self, service):
        for severity in ["low", "medium", "high", "critical"]:
            inc = Incident.objects.create(
                title=f"Test {severity}",
                severity=severity,
                service=service,
            )
            assert inc.severity == severity

    def test_status_choices(self, service):
        for status in ["open", "investigating", "resolved"]:
            inc = Incident.objects.create(
                title=f"Test {status}",
                severity="high",
                status=status,
                service=service,
            )
            assert inc.status == status

    def test_ordering_newest_first(self, service):
        inc1 = Incident.objects.create(title="First", severity="high", service=service)
        # Force inc1 to be 5 seconds older for deterministic ordering
        inc1.created_at = timezone.now() - timedelta(seconds=5)
        inc1.save(update_fields=["created_at"])

        inc2 = Incident.objects.create(title="Second", severity="high", service=service)

        incidents = Incident.objects.all().order_by("-created_at")
        assert incidents[0].id == inc2.id
        assert incidents[1].id == inc1.id

    def test_resolved_at_optional(self, service):
        inc = Incident.objects.create(
            title="Resolved incident",
            severity="medium",
            service=service,
            resolved_at=timezone.now(),
        )
        assert inc.resolved_at is not None

    def test_null_service_allowed(self):
        inc = Incident.objects.create(
            title="Orphan incident",
            severity="low",
        )
        assert inc.service is None
