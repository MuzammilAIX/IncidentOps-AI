"""Diagnosis agent — multi-hypothesis GPT-4 analysis."""
import logging
from ai_engine.llm.client import call_llm, llm_available
from ai_engine.llm.schemas import DiagnosisResult, Hypothesis, TriageResult
from ai_engine.llm.prompts import DIAGNOSIS_SYSTEM, build_diagnosis_prompt

logger = logging.getLogger(__name__)


def diagnose(incident, triage_result: TriageResult, diagnostics: dict) -> DiagnosisResult:
    """Diagnose via GPT-4 multi-hypothesis, or fallback."""
    if not llm_available():
        return _rule_based_diagnosis(incident, triage_result, diagnostics)

    prompt = build_diagnosis_prompt(incident, triage_result, diagnostics)
    result = call_llm(DIAGNOSIS_SYSTEM, prompt, DiagnosisResult, temperature=0.1, agent_name="diagnosis")
    if result is None:
        return _rule_based_diagnosis(incident, triage_result, diagnostics)
    return result


def _rule_based_diagnosis(incident, triage_result, diagnostics) -> DiagnosisResult:
    """Fallback: use rule-based analyze logic."""
    status = diagnostics.get("status", {}) or {}
    container_state = status.get("state", "unknown")
    oom_killed = status.get("oom_killed", False)

    if oom_killed:
        return DiagnosisResult(
            surviving_hypotheses=[Hypothesis(
                hypothesis="Container OOM-killed",
                confidence=0.95,
                evidence_for=["oom_killed=True", f"state={container_state}"],
                evidence_against=[],
                test_needed=None,
            )],
            eliminated_hypotheses=[],
            primary_root_cause="container_oom_killed",
            confidence=0.95,
            reasoning="Container has oom_killed=True flag in Docker status",
        )
    elif container_state == "exited":
        return DiagnosisResult(
            surviving_hypotheses=[Hypothesis(
                hypothesis="Container crashed",
                confidence=0.85,
                evidence_for=[f"state=exited, exit_code={status.get('exit_code')}"],
                evidence_against=[],
                test_needed=None,
            )],
            eliminated_hypotheses=[],
            primary_root_cause="container_crashed",
            confidence=0.85,
            reasoning=f"Container exited with code {status.get('exit_code')}",
        )
    else:
        return DiagnosisResult(
            surviving_hypotheses=[],
            eliminated_hypotheses=[],
            primary_root_cause="insufficient_data",
            confidence=0.3,
            reasoning=f"Container state is '{container_state}', no clear failure signal",
        )

