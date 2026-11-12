
"""Glue between Django and the LangGraph AI workflow."""
from ai_engine.graph import build_graph


def run_investigation(payload: dict) -> dict:
    """
    Run the AI investigation workflow synchronously.

    Args:
        payload: dict with keys: incident_id, service, alert

    Returns:
        dict with keys: incident_id, findings, root_cause, confidence, remediation, steps
    """
    graph = build_graph()
    initial_state = {
        "incident_id": payload.get("incident_id", ""),
        "service": payload.get("service", {}) or {},
        "alert": payload.get("alert", {}) or {},
        "findings": [],
        "steps": [],
    }
    result = graph.invoke(initial_state)
    return result
