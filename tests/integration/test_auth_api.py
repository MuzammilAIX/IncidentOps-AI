"""Integration tests for Auth API."""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestAuthAPI:
    def test_login_success(self, api_client, user):
        response = api_client.post(
            "/api/auth/login/",
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "testuser"
        assert "id" in response.data

    def test_login_invalid_credentials(self, api_client, user):
        response = api_client.post(
            "/api/auth/login/",
            {"username": "testuser", "password": "wrongpass"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_requires_auth(self, api_client):
        response = api_client.get("/api/auth/me/")
        assert response.status_code in (401, 403)

    def test_me_authenticated(self, auth_client, user):
        response = auth_client.get("/api/auth/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "testuser"
        assert response.data["email"] == "test@example.com"

    def test_logout(self, auth_client):
        response = auth_client.post("/api/auth/logout/")
        assert response.status_code == status.HTTP_200_OK
