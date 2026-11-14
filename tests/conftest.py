"""Pytest fixtures for IncidentOps-AI test suite."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.incidents.models import Incident
from apps.investigations.models import Investigation, InvestigationStep
from apps.approvals.models import ApprovalRequest
from apps.services.models import Service


User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def service(db):
    return Service.objects.create(
        name="web-api",
        kind="docker",
        endpoint="http://localhost:8080/health",
    )


@pytest.fixture
def incident(db, service, user):
    return Incident.objects.create(
        title="API returning 500s",
        description="Users reporting errors",
        severity="high",
        status="open",
        service=service,
        created_by=user,
    )


@pytest.fixture
def investigation(db, incident):
    return Investigation.objects.create(
        incident=incident,
        status="done",
        root_cause="container_oom_killed",
        confidence=0.95,
        findings=[
            {"step": "triage", "severity": "high"},
            {"step": "analyze", "root_cause": "container_oom_killed"},
        ],
    )


@pytest.fixture
def approval(db, investigation):
    return ApprovalRequest.objects.create(
        investigation=investigation,
        proposed_actions=[
            {"action": "restart_container", "target": "web-api", "risk": "medium"}
        ],
        status="pending",
    )
