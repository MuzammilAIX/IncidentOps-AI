# Business logic for this app

"""
Investigation persistence services.
"""
from django.utils import timezone
from apps.investigations.models import Investigation, InvestigationStep


def persist_investigation(incident, ai_result: dict) -> Investigation:
    """
    Persist AI investigation results to the database.
    Also auto-creates an ApprovalRequest if remediation actions exist.
    """
    inv = Investigation.objects.create(
        incident=incident,
        status="done",
        root_cause=ai_result.get("root_cause", "") or "",
        confidence=float(ai_result.get("confidence") or 0.0),
        findings=ai_result.get("findings", []) or [],
        finished_at=timezone.now(),
    )

    for step_name in ai_result.get("steps", []) or []:
        InvestigationStep.objects.create(
            investigation=inv,
            name=str(step_name),
            payload={},
        )

    remediation = ai_result.get("remediation", {}) or {}
    actions = remediation.get("actions", []) or []
    if actions:
        from apps.approvals.services import create_approval
        create_approval(inv, actions)

    _audit(incident, inv, ai_result)
    return inv


def _audit(incident, investigation, ai_result):
    from apps.audit.services import log_action
    log_action(
        action="investigation_completed",
        target_type="investigation",
        target_id=str(investigation.id),
        metadata={
            "incident_id": incident.id,
            "root_cause": investigation.root_cause,
            "confidence": investigation.confidence,
            "steps": ai_result.get("steps", []),
        },
    )