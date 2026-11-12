
def run(state: dict) -> dict:
    """Triage step."""
    state.setdefault("steps", []).append("triage")
    return state
