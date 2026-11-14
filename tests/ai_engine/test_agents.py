"""Tests for AI agents with mocked LLM."""
import pytest
from unittest.mock import patch

from ai_engine.agents.triage_agent import triage
from ai_engine.agents.diagnosis_agent import diagnose
from ai_engine.agents.verifier_agent import verify
from ai_engine.agents.remediation_agent import plan_remediation
from ai_engine.llm.schemas import (
    TriageResult, DiagnosisResult, VerificationResult, RemediationPlan,
)


@pytest.fixture
def mock_incident():
    class MockIncident:
        id = 1
        title = "Test incident"
        description = "Test description"
        severity = "high"
        service = None
    return MockIncident()


class TestTriageAgent:
    def test_triage_fallback(self, mock_incident):
        with patch("ai_engine.agents.triage_agent.llm_available", return_value=False):
            result = triage(mock_incident, {"severity": "high"})
            assert isinstance(result, TriageResult)

    def test_critical_maps_to_p1(self, mock_incident):
        mock_incident.severity = "critical"
        with patch("ai_engine.agents.triage_agent.llm_available", return_value=False):
            result = triage(mock_incident, {"severity": "critical"})
            assert result.severity == "P1"


class TestDiagnosisAgent:
    def test_diagnose_fallback_oom(self, mock_incident):
        triage_result = TriageResult(
            severity="P1", affected_scope="API down",
            initial_hypotheses=[], urgency="immediate",
        )
        diagnostics = {
            "status": {"state": "exited", "oom_killed": True, "exit_code": 137},
            "logs": [],
        }
        with patch("ai_engine.agents.diagnosis_agent.llm_available", return_value=False):
            result = diagnose(mock_incident, triage_result, diagnostics)
            assert result.primary_root_cause == "container_oom_killed"

    def test_diagnose_fallback_unknown(self, mock_incident):
        triage_result = TriageResult(
            severity="P3", affected_scope="minor",
            initial_hypotheses=[], urgency="monitor",
        )
        with patch("ai_engine.agents.diagnosis_agent.llm_available", return_value=False):
            result = diagnose(mock_incident, triage_result, {"status": {}})
            assert result.primary_root_cause == "insufficient_data"


class TestVerifierAgent:
    def test_verify_accepts(self, mock_incident):
        diagnosis = DiagnosisResult(
            surviving_hypotheses=[], eliminated_hypotheses=[],
            primary_root_cause="container_oom_killed",
            confidence=0.95, reasoning="OOM evidence",
        )
        with patch("ai_engine.agents.verifier_agent.llm_available", return_value=False):
            result = verify(mock_incident, diagnosis)
            assert result.verified is True


class TestRemediationAgent:
    def test_remediation_fallback(self, mock_incident):
        verification = VerificationResult(
            verified=True, final_root_cause="container_oom_killed", final_confidence=0.9,
        )
        with patch("ai_engine.agents.remediation_agent.llm_available", return_value=False):
            result = plan_remediation(mock_incident, verification)
            assert isinstance(result, RemediationPlan)
            assert len(result.actions) >= 1

    def test_forbidden_actions_filtered(self, mock_incident):
        verification = VerificationResult(
            verified=True, final_root_cause="container_oom_killed", final_confidence=0.9,
        )
        with patch("ai_engine.agents.remediation_agent.llm_available", return_value=False):
            result = plan_remediation(mock_incident, verification)
            for action in result.actions:
                assert action.action not in ["delete_database", "drop_table", "rm_rf"]

    def test_policies_load(self):
        from ai_engine.policies.safety import is_action_allowed
        from ai_engine.policies.execution_rules import ALLOWED_ACTIONS
        assert is_action_allowed("restart_container") is True
        assert is_action_allowed("delete_database") is False
        assert "restart_container" in ALLOWED_ACTIONS
