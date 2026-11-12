
"""
Propose remediation: suggest a safe fix based on root cause.
"""


def run(state: dict) -> dict:
    """Propose remediation actions."""
    root_cause = state.get("root_cause", "unknown")
    service = state.get("service", {}) or {}
    target = service.get("id") or service.get("name") or "unknown"

    plans = {
        "container_crashed": [{
            "action": "restart_container",
            "target": str(target),
            "risk": "low",
            "reason": "Container exited — restart to recover.",
        }],
        "crash_loop": [{
            "action": "restart_container",
            "target": str(target),
            "risk": "medium",
            "reason": "Container restarting repeatedly — restart and observe.",
        }],
    }

    actions = plans.get(root_cause, [])

    finding = {
        "step": "propose_remediation",
        "actions": actions,
        "action_count": len(actions),
    }

    state["remediation"] = {"actions": actions}
    state.setdefault("findings", []).append(finding)
    state.setdefault("steps", []).append("propose_remediation")
    return state
