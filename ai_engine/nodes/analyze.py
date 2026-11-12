
def run(state: dict) -> dict:
    """Analyze step."""
    state.setdefault("steps", []).append("analyze")
    return state
