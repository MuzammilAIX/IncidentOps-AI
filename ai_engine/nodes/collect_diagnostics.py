
def run(state: dict) -> dict:
    """Collect Diagnostics step."""
    state.setdefault("steps", []).append("collect_diagnostics")
    return state
