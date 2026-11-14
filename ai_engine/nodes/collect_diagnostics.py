
# ─── collect_diagnostics.py (ensures status dict is passed) ──────

"""Collect diagnostics using tools."""


def run(state: dict) -> dict:
    service = state.get("service", {}) or {}
    service_id = service.get("id") or service.get("name") or "unknown"

    diagnostics = {"status": {}, "logs": []}

    try:
        from ai_engine.tools.docker_tools import get_container_status, get_container_logs
        status_result = get_container_status.invoke({"service_id": str(service_id)})
        if isinstance(status_result, dict):
            diagnostics["status"] = status_result
        else:
            diagnostics["status"] = {"raw": str(status_result)}

        logs_result = get_container_logs.invoke({"service_id": str(service_id), "lines": 50})
        diagnostics["logs"] = logs_result if isinstance(logs_result, list) else []
    except Exception as e:
        diagnostics["status"] = {"error": str(e)}
        diagnostics["logs"] = []

    finding = {
        "step": "collect_diagnostics",
        "gathered": list(diagnostics.keys()),
        "status_state": diagnostics["status"].get("state", "unknown"),
        "oom_killed": diagnostics["status"].get("oom_killed", False),
    }

    state["diagnostics"] = diagnostics
    state.setdefault("findings", []).append(finding)
    state.setdefault("steps", []).append("collect_diagnostics")
    return state
