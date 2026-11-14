"""Integration tests for Incidents REST API."""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestIncidentsAPI:
    def test_list_requires_auth(self, api_client):
        """Unauthenticated request returns 403."""
        response = api_client.get("/api/incidents/")
        assert response.status_code in (401, 403)

    def test_list_incidents(self, auth_client, incident):
        """Authenticated list returns incidents."""
        response = auth_client.get("/api/incidents/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["title"] == "API returning 500s"

    def test_create_incident(self, auth_client, service):
        """Create incident via POST."""
        response = auth_client.post(
            "/api/incidents/",
            {
                "title": "New incident from API",
                "description": "Testing create",
                "severity": "critical",
                "status": "open",
                "service": service.id,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New incident from API"
        assert response.data["severity"] == "critical"
        assert response.data["created_by"] is not None

    def test_retrieve_incident(self, auth_client, incident):
        """Retrieve single incident by ID."""
        response = auth_client.get(f"/api/incidents/{incident.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == incident.id
        assert response.data["title"] == "API returning 500s"

    def test_update_incident(self, auth_client, incident):
        """Update incident via PATCH."""
        response = auth_client.patch(
            f"/api/incidents/{incident.id}/",
            {"status": "investigating"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "investigating"

    def test_delete_incident(self, auth_client, incident):
        """Delete incident via DELETE."""
        response = auth_client.delete(f"/api/incidents/{incident.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_filter_by_severity(self, auth_client, service):
        """Filter incidents by severity."""
        from apps.incidents.models import Incident
        Incident.objects.create(title="Critical", severity="critical", service=service)
        Incident.objects.create(title="Low", severity="low", service=service)

        response = auth_client.get("/api/incidents/?severity=critical")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["severity"] == "critical"

    def test_filter_by_status(self, auth_client, service):
        """Filter incidents by status."""
        from apps.incidents.models import Incident
        Incident.objects.create(title="Open", severity="high", status="open", service=service)
        Incident.objects.create(title="Resolved", severity="high", status="resolved", service=service)

        response = auth_client.get("/api/incidents/?status=resolved")
        assert response.data["count"] == 1

    def test_search_by_title(self, auth_client, service):
        """Search incidents by title."""
        from apps.incidents.models import Incident
        Incident.objects.create(title="Database issue", severity="high", service=service)
        Incident.objects.create(title="CPU spike", severity="high", service=service)

        response = auth_client.get("/api/incidents/?search=database")
        assert response.data["count"] == 1

    def test_ordering(self, auth_client, service):
        """Order by created_at descending."""
        from apps.incidents.models import Incident
        inc1 = Incident.objects.create(title="First", severity="high", service=service)
        inc2 = Incident.objects.create(title="Second", severity="high", service=service)

        response = auth_client.get("/api/incidents/?ordering=-created_at")
        assert response.data["results"][0]["id"] == inc2.id

    def test_pagination(self, auth_client, service):
        """Pagination returns correct page size."""
        from apps.incidents.models import Incident
        for i in range(15):
            Incident.objects.create(title=f"Incident {i}", severity="high", service=service)

        response = auth_client.get("/api/incidents/?page_size=10")
        assert response.data["count"] == 15
        assert len(response.data["results"]) == 10

    def test_invalid_severity_rejected(self, auth_client, service):
        """Invalid severity returns 400."""
        response = auth_client.post(
            "/api/incidents/",
            {"title": "Bad", "severity": "invalid", "status": "open"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
