
"""
Collect diagnostics: use tools to gather data about the service.
"""
from ai_engine.tools.docker_tools import get_container_status, get_container_logs


def run(state: dict) -> dict:
    """Gather diagnostics from available tools."""
    service = state.get("service", {}) or {}
    service_id = service.get("id") or service.get("name") or "unknown"

    diagnostics = {"status": {}, "logs": []}

    try:
        status_result = get_container_status.invoke({"service_id": str(service_id)})
        diagnostics["status"] = status_result if isinstance(status_result, dict) else {"raw": str(status_result)}
    except Exception as e:
        diagnostics["status"] = {"error": str(e)}

    try:
        logs_result = get_container_logs.invoke({"service_id": str(service_id), "lines": 50})
        diagnostics["logs"] = logs_result if isinstance(logs_result, list) else []
    except Exception as e:
        diagnostics["logs"] = [{"error": str(e)}]

    finding = {
        "step": "collect_diagnostics",
        "gathered": list(diagnostics.keys()),
        "status_state": diagnostics["status"].get("state", "unknown"),
    }

    state["diagnostics"] = diagnostics
    state.setdefault("findings", []).append(finding)
    state.setdefault("steps", []).append("collect_diagnostics")
    return state
