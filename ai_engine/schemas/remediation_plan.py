
from pydantic import BaseModel
from typing import List


class RemediationAction(BaseModel):
    action: str
    target: str
    risk: str = "low"


class RemediationPlan(BaseModel):
    actions: List[RemediationAction] = []
