"""Integration tests for Approvals REST API."""
import pytest
from django.utils import timezone
from rest_framework import status

from apps.approvals.models import ApprovalRequest


@pytest.mark.django_db
class TestApprovalsAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/approvals/")
        assert response.status_code in (401, 403)

    def test_list_approvals(self, auth_client, approval):
        response = auth_client.get("/api/approvals/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["status"] == "pending"

    def test_retrieve_approval(self, auth_client, approval):
        response = auth_client.get(f"/api/approvals/{approval.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == approval.id

    def test_filter_by_status(self, auth_client, investigation):
        ApprovalRequest.objects.create(
            investigation=investigation, proposed_actions=[], status="pending"
        )
        ApprovalRequest.objects.create(
            investigation=investigation, proposed_actions=[], status="approved"
        )

        response = auth_client.get("/api/approvals/?status=pending")
        assert response.data["count"] == 1
        assert response.data["results"][0]["status"] == "pending"

    def test_approve_action(self, auth_client, approval, user):
        """POST /approve/ changes status and sets decided_by."""
        response = auth_client.post(f"/api/approvals/{approval.id}/approve/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "approved"

        approval.refresh_from_db()
        assert approval.status == "approved"
        assert approval.decided_by == user
        assert approval.decided_at is not None

    def test_reject_action(self, auth_client, approval, user):
        """POST /reject/ changes status and sets decided_by."""
        response = auth_client.post(f"/api/approvals/{approval.id}/reject/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "rejected"

        approval.refresh_from_db()
        assert approval.status == "rejected"
        assert approval.decided_by == user

    def test_cannot_approve_non_pending(self, auth_client, investigation):
        """Cannot approve already-approved request."""
        approval = ApprovalRequest.objects.create(
            investigation=investigation, proposed_actions=[], status="approved"
        )
        response = auth_client.post(f"/api/approvals/{approval.id}/approve/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_reject_non_pending(self, auth_client, investigation):
        """Cannot reject already-rejected request."""
        approval = ApprovalRequest.objects.create(
            investigation=investigation, proposed_actions=[], status="rejected"
        )
        response = auth_client.post(f"/api/approvals/{approval.id}/reject/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
