
"""Fake Docker client for local testing."""


class FakeDocker:
    def __init__(self):
        self.containers = {}

    def get_status(self, service_id: str) -> dict:
        return self.containers.get(service_id, {"state": "running"})
