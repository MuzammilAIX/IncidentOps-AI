"""Unit tests for Investigation model."""
import pytest

from apps.investigations.models import Investigation, InvestigationStep


@pytest.mark.django_db
class TestInvestigationModel:
    def test_create_investigation(self, incident):
        inv = Investigation.objects.create(
            incident=incident,
            status="running",
        )
        assert inv.id is not None
        assert inv.status == "running"
        assert inv.incident == incident

    def test_str_representation(self, investigation):
        assert "Investigation<" in str(investigation)

    def test_findings_default_empty_list(self, incident):
        inv = Investigation.objects.create(incident=incident)
        assert inv.findings == []

    def test_confidence_default_zero(self, incident):
        inv = Investigation.objects.create(incident=incident)
        assert inv.confidence == 0.0

    def test_status_choices(self, incident):
        for status in ["running", "done", "failed"]:
            inv = Investigation.objects.create(incident=incident, status=status)
            assert inv.status == status


@pytest.mark.django_db
class TestInvestigationStepModel:
    def test_create_step(self, investigation):
        step = InvestigationStep.objects.create(
            investigation=investigation,
            name="triage",
            payload={"severity": "high"},
        )
        assert step.id is not None
        assert step.name == "triage"

    def test_payload_json(self, investigation):
        step = InvestigationStep.objects.create(
            investigation=investigation,
            name="analyze",
            payload={"root_cause": "oom", "confidence": 0.95},
        )
        step.refresh_from_db()
        assert step.payload["root_cause"] == "oom"
