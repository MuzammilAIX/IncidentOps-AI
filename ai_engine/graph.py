"""
Main LangGraph workflow — Phase 2 with GPT-4 agents.
Flow: triage → collect → diagnose → verify → propose
"""
from langgraph.graph import StateGraph, END
from .state import InvestigationState


def _triage_node(state: dict) -> dict:
    from apps.incidents.models import Incident
    from ai_engine.agents.triage_agent import triage
    from ai_engine.llm.client import llm_available

    incident = Incident.objects.get(id=state["incident_id"])
    result = triage(incident, state.get("alert", {}))

    state["triage_result"] = result.model_dump()
    state["llm_used"] = llm_available()
    state.setdefault("findings", []).append({
        "step": "triage",
        "severity": result.severity,
        "urgency": result.urgency,
        "hypotheses": [h.hypothesis for h in result.initial_hypotheses],
        "llm_used": state["llm_used"],
    })
    state.setdefault("steps", []).append("triage")
    return state


def _collect_node(state: dict) -> dict:
    from ai_engine.nodes import collect_diagnostics
    return collect_diagnostics.run(state)


def _diagnose_node(state: dict) -> dict:
    from apps.incidents.models import Incident
    from ai_engine.agents.diagnosis_agent import diagnose
    from ai_engine.llm.schemas import TriageResult

    incident = Incident.objects.get(id=state["incident_id"])
    triage_result = TriageResult(**state["triage_result"])
    result = diagnose(incident, triage_result, state.get("diagnostics", {}))

    state["diagnosis_result"] = result.model_dump()
    state["root_cause"] = result.primary_root_cause
    state["confidence"] = result.confidence
    state.setdefault("findings", []).append({
        "step": "diagnose",
        "primary_root_cause": result.primary_root_cause,
        "confidence": result.confidence,
        "reasoning": result.reasoning,
        "surviving_count": len(result.surviving_hypotheses),
        "eliminated_count": len(result.eliminated_hypotheses),
    })
    state.setdefault("steps", []).append("diagnose")
    return state


def _verify_node(state: dict) -> dict:
    from apps.incidents.models import Incident
    from ai_engine.agents.verifier_agent import verify
    from ai_engine.llm.schemas import DiagnosisResult

    incident = Incident.objects.get(id=state["incident_id"])
    diagnosis = DiagnosisResult(**state["diagnosis_result"])
    result = verify(incident, diagnosis)

    state["verification_result"] = result.model_dump()
    state["root_cause"] = result.final_root_cause
    state["confidence"] = result.final_confidence
    state.setdefault("findings", []).append({
        "step": "verify",
        "verified": result.verified,
        "final_root_cause": result.final_root_cause,
        "final_confidence": result.final_confidence,
    })
    state.setdefault("steps", []).append("verify")
    return state


def _propose_node(state: dict) -> dict:
    from apps.incidents.models import Incident
    from ai_engine.agents.remediation_agent import plan_remediation
    from ai_engine.llm.schemas import VerificationResult

    incident = Incident.objects.get(id=state["incident_id"])
    verification = VerificationResult(**state["verification_result"])
    result = plan_remediation(incident, verification)

    state["remediation"] = {
        "actions": [a.model_dump() for a in result.actions],
        "requires_approval": result.requires_approval,
        "estimated_duration": result.estimated_duration,
    }
    state.setdefault("findings", []).append({
        "step": "propose_remediation",
        "action_count": len(result.actions),
        "estimated_duration": result.estimated_duration,
    })
    state.setdefault("steps", []).append("propose_remediation")
    return state


def build_graph():
    g = StateGraph(InvestigationState)
    g.add_node("triage", _triage_node)
    g.add_node("collect", _collect_node)
    g.add_node("diagnose", _diagnose_node)
    g.add_node("verify", _verify_node)
    g.add_node("propose", _propose_node)

    g.set_entry_point("triage")
    g.add_edge("triage", "collect")
    g.add_edge("collect", "diagnose")
    g.add_edge("diagnose", "verify")
    g.add_edge("verify", "propose")
    g.add_edge("propose", END)

    return g.compile()
