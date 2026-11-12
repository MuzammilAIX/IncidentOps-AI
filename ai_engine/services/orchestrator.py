
"""Glue between Django and the LangGraph AI workflow."""
from ai_engine.graph import build_graph


def run_investigation(payload: dict) -> dict:
    graph = build_graph()
    result = graph.invoke(payload)
    return result
