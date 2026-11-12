
"""Connector to kubernetes."""
from integrations.base import BaseConnector


class KubernetesConnector(BaseConnector):
    def health_check(self) -> bool:
        return True

    def get_status(self, service_id: str) -> dict:
        return {"service_id": service_id, "state": "unknown"}
