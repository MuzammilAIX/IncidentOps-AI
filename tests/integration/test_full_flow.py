"""End-to-end flow tests: incident → investigation → approval → decision."""
import pytest
from django.utils import timezone
from rest_framework import status

from apps.incidents.models import Incident
from apps.investigations.models import Investigation
from apps.approvals.models import ApprovalRequest


@pytest.mark.django_db
class TestFullFlow:
    def test_incident_to_approval_flow(self, auth_client, service):
        """Full pipeline: create incident → attach investigation → approval."""
        # Step 1: Create incident via API
        r1 = auth_client.post(
            "/api/incidents/",
            {"title": "Pipeline test", "severity": "high", "status": "open", "service": service.id},
            format="json",
        )
        assert r1.status_code == status.HTTP_201_CREATED
        incident_id = r1.data["id"]

        # Step 2: Directly create investigation (as AI would)
        incident = Incident.objects.get(id=incident_id)
        investigation = Investigation.objects.create(
            incident=incident,
            status="done",
            root_cause="container_oom_killed",
            confidence=0.9,
            findings=[{"step": "triage"}, {"step": "analyze"}],
            finished_at=timezone.now(),
        )

        # Step 3: Create approval
        approval = ApprovalRequest.objects.create(
            investigation=investigation,
            proposed_actions=[{"action": "restart_container", "target": "web-api"}],
            status="pending",
        )

        # Step 4: Verify chain via API
        r2 = auth_client.get(f"/api/investigations/{investigation.id}/")
        assert r2.status_code == status.HTTP_200_OK
        assert r2.data["root_cause"] == "container_oom_killed"

        r3 = auth_client.get(f"/api/approvals/{approval.id}/")
        assert r3.status_code == status.HTTP_200_OK
        assert r3.data["status"] == "pending"

        # Step 5: Approve via API
        r4 = auth_client.post(f"/api/approvals/{approval.id}/approve/")
        assert r4.status_code == status.HTTP_200_OK
        assert r4.data["status"] == "approved"

    def test_multiple_incidents_isolated(self, auth_client, service):
        """Multiple incidents are properly isolated."""
        from apps.incidents.models import Incident
        i1 = Incident.objects.create(title="Incident 1", severity="high", service=service)
        i2 = Incident.objects.create(title="Incident 2", severity="low", service=service)

        r = auth_client.get("/api/incidents/")
        assert r.data["count"] == 2

        # Filter returns only matching
        r = auth_client.get("/api/incidents/?severity=high")
        assert r.data["count"] == 1
        assert r.data["results"][0]["id"] == i1.id

    def test_approval_workflow_status_transitions(self, auth_client, investigation):
        """Approval status transitions: pending → approved."""
        approval = ApprovalRequest.objects.create(
            investigation=investigation,
            proposed_actions=[],
            status="pending",
        )

        # Approve
        r = auth_client.post(f"/api/approvals/{approval.id}/approve/")
        assert r.status_code == status.HTTP_200_OK

        # Cannot re-approve
        r2 = auth_client.post(f"/api/approvals/{approval.id}/approve/")
        assert r2.status_code == status.HTTP_400_BAD_REQUEST

    def test_investigation_steps_persist(self, auth_client, incident):
        """Investigation steps are saved and retrievable."""
        from apps.investigations.models import Investigation, InvestigationStep

        inv = Investigation.objects.create(incident=incident, status="done")
        for step_name in ["triage", "diagnose", "propose"]:
            InvestigationStep.objects.create(
                investigation=inv, name=step_name, payload={"step": step_name}
            )

        r = auth_client.get(f"/api/investigations/{inv.id}/")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["step_count"] == 3
