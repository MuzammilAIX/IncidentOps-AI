"""Pydantic schemas for structured LLM output."""
from typing import List, Optional
from pydantic import BaseModel, Field


class Hypothesis(BaseModel):
    """A single hypothesis about the incident root cause."""
    hypothesis: str = Field(description="Clear statement of the hypothesis")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence 0-1")
    evidence_for: List[str] = Field(default_factory=list, description="Evidence supporting")
    evidence_against: List[str] = Field(default_factory=list, description="Evidence against")
    test_needed: Optional[str] = Field(None, description="What evidence would falsify this")


class TriageResult(BaseModel):
    """Triage agent output."""
    severity: str = Field(description="P1, P2, P3, or P4")
    affected_scope: str = Field(description="Brief description of affected services")
    initial_hypotheses: List[Hypothesis] = Field(default_factory=list)
    urgency: str = Field(description="immediate, soon, or monitor")


class DiagnosisResult(BaseModel):
    """Diagnosis agent output."""
    surviving_hypotheses: List[Hypothesis] = Field(default_factory=list)
    eliminated_hypotheses: List[Hypothesis] = Field(default_factory=list)
    primary_root_cause: str = Field(description="Most likely root cause")
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(description="Why this root cause was chosen")


class VerificationResult(BaseModel):
    """Verifier agent output."""
    verified: bool
    final_root_cause: str
    final_confidence: float = Field(ge=0.0, le=1.0)
    falsification_attempts: List[str] = Field(default_factory=list)
    remaining_doubts: List[str] = Field(default_factory=list)


class RemediationAction(BaseModel):
    """A single remediation action."""
    id: str = Field(description="Unique ID, e.g., opt_1")
    action: str = Field(description="restart_container, scale_replicas, rollback, etc.")
    target: str = Field(description="Service or resource")
    risk: str = Field(description="low, medium, high")
    reason: str = Field(description="Why this helps")
    expected_outcome: str = Field(description="What should happen")
    rollback_plan: str = Field(description="How to undo if it fails")
    confidence: float = Field(ge=0.0, le=1.0)


class RemediationPlan(BaseModel):
    """Remediation agent output."""
    root_cause_summary: str
    actions: List[RemediationAction] = Field(default_factory=list)
    requires_approval: bool = True
    estimated_duration: str = Field(description="e.g., ~2 minutes")
