
"""
Main LangGraph workflow.
Flow: triage -> collect_diagnostics -> analyze -> propose_remediation
"""
from langgraph.graph import StateGraph, END
from .state import InvestigationState
from .nodes import triage, collect_diagnostics, analyze, propose_remediation


def build_graph():
    g = StateGraph(InvestigationState)
    g.add_node("triage", triage.run)
    g.add_node("collect", collect_diagnostics.run)
    g.add_node("analyze", analyze.run)
    g.add_node("propose", propose_remediation.run)

    g.set_entry_point("triage")
    g.add_edge("triage", "collect")
    g.add_edge("collect", "analyze")
    g.add_edge("analyze", "propose")
    g.add_edge("propose", END)

    return g.compile()