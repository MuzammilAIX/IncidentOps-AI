"""Execution rules - what AI can and cannot do."""

ALLOWED_ACTIONS = {
    "restart_container",
    "scale_replicas",
    "rollback_deployment",
    "rollback",
    "drain_node",
    "increase_memory_limit",
    "restart_pod",
}


def requires_approval(action: str) -> bool:
    return True
