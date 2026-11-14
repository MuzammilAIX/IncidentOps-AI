from typing import TypedDict, Optional, List


class InvestigationState(TypedDict, total=False):
    """Shared state passed between LangGraph nodes."""
    incident_id: str
    service: dict
    alert: dict
    diagnostics: dict
    findings: list
    root_cause: Optional[str]
    confidence: Optional[float]
    remediation: Optional[dict]
    steps: list
    triage_result: Optional[dict]
    diagnosis_result: Optional[dict]
    verification_result: Optional[dict]
    llm_used: bool
