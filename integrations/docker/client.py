
"""Connector to Docker."""
from integrations.base import BaseConnector


class DockerConnector(BaseConnector):
    def health_check(self) -> bool:
        return True

    def get_status(self, service_id: str) -> dict:
        return {"service_id": service_id, "state": "unknown"}

    def get_logs(self, service_id: str, lines: int = 100) -> list:
        return []
