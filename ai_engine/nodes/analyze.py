# ─── analyze.py (OOM detection) ──────────────────────────────────

"""Analyze node — real RCA from real diagnostics."""


def run(state: dict) -> dict:
    diagnostics = state.get("diagnostics", {}) or {}
    status = diagnostics.get("status", {}) or {}
    logs = diagnostics.get("logs", []) or []

    container_state = status.get("state", "unknown")
    exit_code = status.get("exit_code")
    oom_killed = status.get("oom_killed", False)
    restart_count = status.get("restart_count", 0)

    log_text = " ".join(
        entry.get("line", "") if isinstance(entry, dict) else str(entry)
        for entry in logs
    ).lower()

    root_cause = "unknown"
    confidence = 0.5
    evidence = {}

    if container_state == "exited":
        if oom_killed:
            root_cause = "container_oom_killed"
            confidence = 0.95
            evidence["oom_killed"] = True
        elif exit_code is not None and exit_code != 0:
            root_cause = "container_crashed"
            confidence = 0.85
            evidence["exit_code"] = exit_code
        else:
            root_cause = "container_exited"
            confidence = 0.7

    elif container_state == "restarting" or restart_count > 3:
        root_cause = "crash_loop"
        confidence = 0.8
        evidence["restart_count"] = restart_count

    elif "out of memory" in log_text or "oom" in log_text:
        root_cause = "container_oom_killed"
        confidence = 0.85
        evidence["log_pattern"] = "oom"

    elif "connection refused" in log_text:
        root_cause = "dependency_unavailable"
        confidence = 0.75
        evidence["log_pattern"] = "connection_refused"

    elif "timeout" in log_text:
        root_cause = "timeout"
        confidence = 0.7
        evidence["log_pattern"] = "timeout"

    elif container_state == "unknown":
        root_cause = "insufficient_data"
        confidence = 0.3

    finding = {
        "step": "analyze",
        "root_cause": root_cause,
        "confidence": confidence,
        "evidence": evidence,
        "container_state": container_state,
    }

    state["root_cause"] = root_cause
    state["confidence"] = confidence
    state.setdefault("findings", []).append(finding)
    state.setdefault("steps", []).append("analyze")
    return state
