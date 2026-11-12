
from langchain_core.tools import tool
from integrations.docker.client import DockerConnector


@tool
def get_container_status(service_id: str) -> dict:
    """Return Docker container status for a service."""
    return DockerConnector().get_status(service_id)


@tool
def get_container_logs(service_id: str, lines: int = 100) -> list:
    """Return recent Docker logs for a service."""
    return DockerConnector().get_logs(service_id, lines=lines)
