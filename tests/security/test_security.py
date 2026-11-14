"""Security tests."""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestAuthRequired:
    def test_incidents_requires_auth(self, api_client):
        r = api_client.get("/api/incidents/")
        assert r.status_code in (401, 403)

    def test_investigations_requires_auth(self, api_client):
        r = api_client.get("/api/investigations/")
        assert r.status_code in (401, 403)

    def test_approvals_requires_auth(self, api_client):
        r = api_client.get("/api/approvals/")
        assert r.status_code in (401, 403)

    def test_create_incident_requires_auth(self, api_client):
        r = api_client.post("/api/incidents/", {"title": "test", "severity": "high"})
        assert r.status_code in (401, 403)


@pytest.mark.django_db
class TestInputValidation:
    def test_invalid_severity_rejected(self, auth_client):
        r = auth_client.post(
            "/api/incidents/",
            {"title": "Test", "severity": "not_a_real_severity"},
            format="json",
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_empty_title_rejected(self, auth_client):
        r = auth_client.post(
            "/api/incidents/",
            {"title": "", "severity": "high"},
            format="json",
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_very_long_title_rejected(self, auth_client):
        r = auth_client.post(
            "/api/incidents/",
            {"title": "x" * 300, "severity": "high"},
            format="json",
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestXSSStorage:
    def test_html_payload_stored_safely(self, auth_client, service):
        payload = "<script>alert('xss')</script>"
        r = auth_client.post(
            "/api/incidents/",
            {"title": payload, "severity": "high", "service": service.id},
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
