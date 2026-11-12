
"""
Triage node: classify incident severity and extract signals.
"""


def run(state: dict) -> dict:
    """Classify the incoming incident."""
    alert = state.get("alert", {}) or {}
    service = state.get("service", {}) or {}

    severity = alert.get("severity", "medium").lower()
    if severity not in ("low", "medium", "high", "critical"):
        severity = "medium"

    finding = {
        "step": "triage",
        "severity": severity,
        "service": service.get("id") or service.get("name") or "unknown",
        "note": f"Incident classified as {severity}",
    }

    state.setdefault("findings", []).append(finding)
    state.setdefault("steps", []).append("triage")
    state["triage"] = {"severity": severity}
    return state
