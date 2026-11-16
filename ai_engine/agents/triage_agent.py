"""Triage agent - GPT-4 classification or rule-based fallback."""
from ai_engine.llm.client import call_llm, llm_available
from ai_engine.llm.schemas import TriageResult, Hypothesis
from ai_engine.llm.prompts import TRIAGE_SYSTEM


def triage(incident, alert: dict) -> TriageResult:
    if not llm_available():
        return _rule_based_triage(incident, alert)

    prompt = "Incident: " + incident.title
    prompt += chr(10) + "Severity: " + incident.severity
    prompt += chr(10) + "Alert: " + str(alert)
    prompt += chr(10) + chr(10) + "Triage this incident."

    result = call_llm(TRIAGE_SYSTEM, prompt, TriageResult, agent_name="triage")
    if result is None:
        return _rule_based_triage(incident, alert)
    return result


def _rule_based_triage(incident, alert: dict) -> TriageResult:
    sev_map = {"critical": "P1", "high": "P2", "medium": "P3", "low": "P4"}
    severity = sev_map.get(incident.severity, "P3")

    hypotheses = []
    text = (incident.title + " " + (incident.description or "")).lower()
    if "oom" in text:
        hypotheses.append(Hypothesis(
            hypothesis="Container was OOM-killed",
            confidence=0.6,
            evidence_for=["Incident mentions OOM"],
            evidence_against=[],
            test_needed="Check container oom_killed flag",
        ))
    hypotheses.append(Hypothesis(
        hypothesis="Service is unhealthy or crashed",
        confidence=0.4,
        evidence_for=["Incident exists"],
        evidence_against=[],
        test_needed="Check container status",
    ))

    service_name = incident.service.name if incident.service else "unknown"
    return TriageResult(
        severity=severity,
        affected_scope="Service: " + service_name,
        initial_hypotheses=hypotheses,
        urgency="immediate" if severity == "P1" else "soon",
    )

