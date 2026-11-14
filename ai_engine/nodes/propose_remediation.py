
# ─── propose_remediation.py (context-aware plans) ────────────────

"""Propose remediation — context-aware plans."""


def run(state: dict) -> dict:
    root_cause = state.get("root_cause", "unknown")
    service = state.get("service", {}) or {}
    target = service.get("id") or service.get("name") or "unknown"

    plans = {
        "container_crashed": [{
            "action": "restart_container",
            "target": str(target),
            "risk": "low",
            "reason": "Container exited with error — restart to recover.",
        }],
        "container_oom_killed": [{
            "action": "restart_container",
            "target": str(target),
            "risk": "medium",
            "reason": "Container OOM-killed — restart, then investigate memory limits.",
        }],
        "crash_loop": [{
            "action": "restart_container",
            "target": str(target),
            "risk": "medium",
            "reason": "Crash loop detected — restart with observation.",
        }],
        "dependency_unavailable": [{
            "action": "restart_container",
            "target": str(target),
            "risk": "low",
            "reason": "Dependency unavailable — restart may reconnect.",
        }],
        "timeout": [{
            "action": "restart_container",
            "target": str(target),
            "risk": "low",
            "reason": "Service timing out — restart to clear hung state.",
        }],
    }

    actions = plans.get(root_cause, [])
    state["remediation"] = {"actions": actions}

    state.setdefault("findings", []).append({
        "step": "propose_remediation",
        "action_count": len(actions),
        "actions": actions,
    })
    state.setdefault("steps", []).append("propose_remediation")
    return state
