# Business logic for this app

"""
Audit service: append-only activity log.
"""


def log_action(action: str, target_type: str, target_id: str, metadata: dict = None, actor=None):
    """Write an audit log entry."""
    from apps.audit.models import AuditLog

    return AuditLog.objects.create(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=target_id,
        metadata=metadata or {},
    )
