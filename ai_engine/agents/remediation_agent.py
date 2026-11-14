"""Remediation agent — GPT-4 or fallback plan generation."""
from ai_engine.llm.client import call_llm, llm_available
from ai_engine.llm.schemas import (
    RemediationPlan, RemediationAction, VerificationResult
)
from ai_engine.llm.prompts import REMEDIATION_SYSTEM, build_remediation_prompt
from ai_engine.policies.safety import is_action_allowed
from ai_engine.policies.execution_rules import ALLOWED_ACTIONS


def plan_remediation(
    incident,
    verification: VerificationResult,
    service_names: list = None,
) -> RemediationPlan:
    """Generate remediation plan."""
    if not llm_available():
        return _rule_based_remediation(incident, verification)

    prompt = build_remediation_prompt(incident, verification, service_names or [])
    result = call_llm(REMEDIATION_SYSTEM, prompt, RemediationPlan, temperature=0.3)

    if result is None:
        return _rule_based_remediation(incident, verification)

    safe_actions = [
        a for a in result.actions
        if a.action in ALLOWED_ACTIONS and is_action_allowed(a.action)
    ]
    result.actions = safe_actions
    result.requires_approval = True
    return result


def _rule_based_remediation(incident, verification) -> RemediationPlan:
    """Fallback: existing rule-based plans."""
    root_cause = verification.final_root_cause
    target = incident.service.name if incident.service else "unknown"

    plans = {
        "container_oom_killed": [
            RemediationAction(
                id="opt_1",
                action="restart_container",
                target=target,
                risk="medium",
                reason="Container OOM-killed — restart will recover temporarily",
                expected_outcome="Container returns to running state",
                rollback_plan="If restart fails, escalate to memory limit increase",
                confidence=0.85,
            ),
        ],
        "container_crashed": [
            RemediationAction(
                id="opt_1",
                action="restart_container",
                target=target,
                risk="low",
                reason="Container exited with error — restart to recover",
                expected_outcome="Container returns to running state",
                rollback_plan="If restart fails, investigate root cause before retrying",
                confidence=0.85,
            ),
        ],
    }

    actions = plans.get(root_cause, [])
    return RemediationPlan(
        root_cause_summary=verification.final_root_cause,
        actions=actions,
        requires_approval=True,
        estimated_duration="~1 minute" if actions else "N/A",
    )
