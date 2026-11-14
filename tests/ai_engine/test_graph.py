"""Tests for LangGraph workflow."""
import pytest


class TestGraphStructure:
    def test_graph_builds(self):
        from ai_engine.graph import build_graph
        graph = build_graph()
        assert graph is not None

    def test_state_import(self):
        from ai_engine.state import InvestigationState
        assert InvestigationState is not None


class TestOrchestrator:
    def test_orchestrator_imports(self):
        from ai_engine.services.orchestrator import run_investigation
        assert callable(run_investigation)

    def test_orchestrator_has_build_graph(self):
        from ai_engine.services import orchestrator
        assert hasattr(orchestrator, "run_investigation")
