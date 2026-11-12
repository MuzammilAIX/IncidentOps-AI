# Business logic for this app

"""
Approval services: auto-create approval requests from AI proposals.
"""


def create_approval(investigation, actions: list):
    """Create an ApprovalRequest from AI-proposed actions."""
    from apps.approvals.models import ApprovalRequest
    from apps.audit.services import log_action

    approval = ApprovalRequest.objects.create(
        investigation=investigation,
        proposed_actions=actions,
        status="pending",
    )

    log_action(
        action="approval_created",
        target_type="approval",
        target_id=str(approval.id),
        metadata={
            "investigation_id": investigation.id,
            "action_count": len(actions),
        },
    )
    return approval
