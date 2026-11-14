
"""Docker tools for the AI agent."""
import os
from langchain_core.tools import tool

USE_SIMULATOR = os.getenv("USE_SIMULATOR", "1") == "1"


def _get_docker():
    if USE_SIMULATOR:
        from simulator.services.fake_docker import FakeDocker
        # Shared instance so simulator state persists between calls
        if not hasattr(_get_docker, "_instance"):
            _get_docker._instance = FakeDocker()
        return _get_docker._instance
    from integrations.docker.client import DockerConnector
    return DockerConnector()


@tool
def get_container_status(service_id: str) -> dict:
    """Return container status for a service."""
    return _get_docker().get_status(service_id)


@tool
def get_container_logs(service_id: str, lines: int = 50) -> list:
    """Return recent container logs for a service."""
    return _get_docker().get_logs(service_id, lines=lines)