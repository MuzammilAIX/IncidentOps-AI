
from langchain_core.tools import tool
from integrations.prometheus.client import PrometheusConnector


@tool
def query_metric(query: str) -> dict:
    """Run a PromQL query and return the result."""
    return PrometheusConnector().query(query)


@tool
def get_active_alerts() -> list:
    """Return currently firing alerts."""
    return PrometheusConnector().get_alerts()
