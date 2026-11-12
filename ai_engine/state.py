
from typing import TypedDict, Optional


class InvestigationState(TypedDict, total=False):
    incident_id: str
    service: dict
    alert: dict
    diagnostics: dict
    findings: list
    root_cause: Optional[str]
    confidence: Optional[float]
    remediation: Optional[dict]
    steps: list
