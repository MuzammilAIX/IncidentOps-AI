
from pydantic import BaseModel
from typing import Optional, List


class InvestigationResult(BaseModel):
    incident_id: str
    root_cause: Optional[str] = None
    confidence: float = 0.0
    findings: List[dict] = []
