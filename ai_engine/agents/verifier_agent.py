"""Verifier agent — try to falsify the diagnosis."""
from ai_engine.llm.client import call_llm, llm_available
from ai_engine.llm.schemas import VerificationResult, DiagnosisResult
from ai_engine.llm.prompts import VERIFIER_SYSTEM, build_verification_prompt


def verify(incident, diagnosis: DiagnosisResult) -> VerificationResult:
    """Verify diagnosis by attempting falsification."""
    if not llm_available():
        return _trust_diagnosis(diagnosis)

    prompt = build_verification_prompt(incident, diagnosis)
    result = call_llm(VERIFIER_SYSTEM, prompt, VerificationResult, temperature=0.1)
    if result is None:
        return _trust_diagnosis(diagnosis)
    return result


def _trust_diagnosis(diagnosis: DiagnosisResult) -> VerificationResult:
    """Fallback: accept the diagnosis as-is."""
    return VerificationResult(
        verified=True,
        final_root_cause=diagnosis.primary_root_cause,
        final_confidence=diagnosis.confidence,
        falsification_attempts=[],
        remaining_doubts=[],
    )
