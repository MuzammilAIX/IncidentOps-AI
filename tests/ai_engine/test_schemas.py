"""Tests for AI engine Pydantic schemas."""
import pytest
from pydantic import ValidationError

from ai_engine.llm.schemas import (
    Hypothesis, TriageResult, DiagnosisResult,
    VerificationResult, RemediationAction, RemediationPlan,
)


class TestHypothesis:
    def test_valid_hypothesis(self):
        h = Hypothesis(
            hypothesis="Container OOM-killed",
            confidence=0.9,
            evidence_for=["oom_killed=True"],
            evidence_against=[],
            test_needed=None,
        )
        assert h.hypothesis == "Container OOM-killed"
        assert h.confidence == 0.9

    def test_confidence_must_be_between_0_and_1(self):
        with pytest.raises(ValidationError):
            Hypothesis(hypothesis="test", confidence=1.5)
        with pytest.raises(ValidationError):
            Hypothesis(hypothesis="test", confidence=-0.1)


class TestTriageResult:
    def test_valid_triage(self):
        t = TriageResult(
            severity="P1",
            affected_scope="API is down",
            initial_hypotheses=[],
            urgency="immediate",
        )
        assert t.severity == "P1"


class TestDiagnosisResult:
    def test_valid_diagnosis(self):
        d = DiagnosisResult(
            surviving_hypotheses=[],
            eliminated_hypotheses=[],
            primary_root_cause="container_oom_killed",
            confidence=0.95,
            reasoning="Container oom_killed flag set",
        )
        assert d.primary_root_cause == "container_oom_killed"


class TestVerificationResult:
    def test_valid_verification(self):
        v = VerificationResult(
            verified=True,
            final_root_cause="container_oom_killed",
            final_confidence=0.9,
        )
        assert v.verified is True


class TestRemediationPlan:
    def test_valid_plan(self):
        plan = RemediationPlan(
            root_cause_summary="OOM killed",
            actions=[
                RemediationAction(
                    id="opt_1",
                    action="restart_container",
                    target="web-api",
                    risk="medium",
                    reason="Recover from OOM",
                    expected_outcome="Container running",
                    rollback_plan="Check health",
                    confidence=0.85,
                )
            ],
            requires_approval=True,
            estimated_duration="~1 minute",
        )
        assert len(plan.actions) == 1
