
"""
Analyze node: determine root cause from collected diagnostics.
"""


def run(state: dict) -> dict:
    """Determine root cause with confidence."""
    diagnostics = state.get("diagnostics", {}) or {}
    status = diagnostics.get("status", {}) or {}
    container_state = status.get("state", "unknown")

    if container_state == "exited":
        root_cause = "container_crashed"
        confidence = 0.85
    elif container_state == "unknown":
        root_cause = "insufficient_data"
        confidence = 0.30
    elif container_state == "restarting":
        root_cause = "crash_loop"
        confidence = 0.75
    else:
        root_cause = "unknown"
        confidence = 0.50

    finding = {
        "step": "analyze",
        "root_cause": root_cause,
        "confidence": confidence,
        "evidence": {"container_state": container_state},
    }

    state["root_cause"] = root_cause
    state["confidence"] = confidence
    state.setdefault("findings", []).append(finding)
    state.setdefault("steps", []).append("analyze")
    return state
