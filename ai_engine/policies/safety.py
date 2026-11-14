"""AI safety rules - block dangerous actions."""

FORBIDDEN_ACTIONS = {
    "delete_database",
    "drop_table",
    "rm_rf",
    "shutdown_cluster",
}


def is_action_allowed(action: str) -> bool:
    return action not in FORBIDDEN_ACTIONS
