"""Tests for AI orchestrator with mocked graph."""
from unittest.mock import patch, MagicMock


class TestOrchestratorFallback:
    def test_orchestrator_with_mocked_graph(self):
        from ai_engine.services.orchestrator import run_investigation

        with patch("ai_engine.services.orchestrator.build_graph") as mock_build:
            mock_graph = MagicMock()
            mock_graph.invoke.return_value = {
                "root_cause": "container_oom_killed",
                "confidence": 0.95,
                "findings": [],
                "steps": ["triage", "collect_diagnostics", "analyze", "verify", "propose_remediation"],
                "remediation": {"actions": []},
            }
            mock_build.return_value = mock_graph

            result = run_investigation({
                "incident_id": "1",
                "service": {"id": "web-api"},
                "alert": {"severity": "high"},
            })

            assert result["root_cause"] == "container_oom_killed"

    def test_orchestrator_handles_empty_service(self):
        from ai_engine.services.orchestrator import run_investigation

        with patch("ai_engine.services.orchestrator.build_graph") as mock_build:
            mock_graph = MagicMock()
            mock_graph.invoke.return_value = {"root_cause": "unknown", "confidence": 0.5}
            mock_build.return_value = mock_graph

            result = run_investigation({"incident_id": "1"})
            assert "root_cause" in result

    def test_orchestrator_callable(self):
        from ai_engine.services.orchestrator import run_investigation
        assert callable(run_investigation)
