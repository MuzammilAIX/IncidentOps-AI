"""Unit tests for ApprovalRequest model."""
import pytest

from apps.approvals.models import ApprovalRequest


@pytest.mark.django_db
class TestApprovalRequestModel:
    def test_create_approval(self, investigation):
        approval = ApprovalRequest.objects.create(
            investigation=investigation,
            proposed_actions=[{"action": "restart_container", "target": "web-api"}],
            status="pending",
        )
        assert approval.id is not None
        assert approval.status == "pending"
        assert len(approval.proposed_actions) == 1

    def test_status_choices(self, investigation):
        for status in ["pending", "approved", "rejected"]:
            approval = ApprovalRequest.objects.create(
                investigation=investigation,
                proposed_actions=[],
                status=status,
            )
            assert approval.status == status

    def test_default_pending(self, investigation):
        approval = ApprovalRequest.objects.create(
            investigation=investigation,
            proposed_actions=[],
        )
        assert approval.status == "pending"

    def test_decided_by_nullable(self, investigation):
        approval = ApprovalRequest.objects.create(
            investigation=investigation,
            proposed_actions=[],
        )
        assert approval.decided_by is None
        assert approval.decided_at is None
