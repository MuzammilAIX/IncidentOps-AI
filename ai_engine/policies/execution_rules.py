
"""Execution rules — what AI can and cannot do."""

ALLOWED_ACTIONS = {
    "restart_container",
    "scale_replicas",
    "rollback_deployment",
}


def requires_approval(action: str) -> bool:
    return True  # everything state-changing needs approval
