
from langchain_core.tools import tool


@tool
def search_logs(service_id: str, pattern: str) -> list:
    """Search service logs for a pattern."""
    return []
