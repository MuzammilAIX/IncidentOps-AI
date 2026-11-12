
"""Connector to Prometheus."""
from integrations.base import BaseConnector


class PrometheusConnector(BaseConnector):
    def health_check(self) -> bool:
        return True

    def get_status(self, service_id: str) -> dict:
        return {"service_id": service_id, "state": "unknown"}

    def query(self, promql: str) -> dict:
        return {"query": promql, "result": []}

    def get_alerts(self) -> list:
        return []
