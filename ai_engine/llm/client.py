"""
LLM client — OpenAI wrapper with fallback to rule-based + observability tracing.
"""
import os
import json
import time
import logging
from typing import Optional, Type, TypeVar
from pydantic import BaseModel

from ai_engine.llm.tracing import get_current_investigation

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

_llm_available: Optional[bool] = None


def llm_available() -> bool:
    global _llm_available
    if _llm_available is not None:
        return _llm_available
    if not os.getenv("OPENAI_API_KEY"):
        _llm_available = False
        return False
    try:
        import openai
        _llm_available = True
        return True
    except ImportError:
        _llm_available = False
        return False


def get_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _record_llm_call(agent_name, model, usage, latency_ms, success=True, error_message=""):
    """Record an LLM call for observability. Never raises."""
    try:
        from apps.monitoring.models import LLMCall
        inv_id = get_current_investigation()
        LLMCall.objects.create(
            investigation_id=inv_id,
            agent_name=agent_name,
            model=model,
            prompt_tokens=getattr(usage, "prompt_tokens", 0) if usage else 0,
            completion_tokens=getattr(usage, "completion_tokens", 0) if usage else 0,
            total_tokens=getattr(usage, "total_tokens", 0) if usage else 0,
            latency_ms=latency_ms,
            success=success,
            error_message=error_message[:1000] if error_message else "",
        )
    except Exception as e:
        logger.warning("Failed to record LLM call: %s", e)


def _prepare_strict_schema(schema: dict) -> dict:
    if not isinstance(schema, dict):
        return schema
    result = {}
    for key, value in schema.items():
        if key == "properties" and isinstance(value, dict):
            result[key] = {p: _prepare_strict_schema(s) for p, s in value.items()}
        elif key == "items" and isinstance(value, dict):
            result[key] = _prepare_strict_schema(value)
        elif key in ("anyOf", "oneOf", "allOf") and isinstance(value, list):
            result[key] = [_prepare_strict_schema(v) for v in value]
        elif key == "$defs" and isinstance(value, dict):
            result[key] = {n: _prepare_strict_schema(s) for n, s in value.items()}
        else:
            result[key] = value
    if "properties" in result:
        result["additionalProperties"] = False
        result["required"] = list(result["properties"].keys())
    return result


def call_llm(system, user, schema, temperature=0.2, max_tokens=2000, agent_name="other"):
    if not llm_available():
        logger.info("LLM not available — skipping call")
        return None

    model = get_model()
    start = time.time()
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        raw_schema = schema.model_json_schema()
        strict_schema = _prepare_strict_schema(raw_schema)
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={
                "type": "json_schema",
                "json_schema": {"name": schema.__name__, "strict": True, "schema": strict_schema},
            },
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        latency_ms = int((time.time() - start) * 1000)
        _record_llm_call(agent_name, model, response.usage, latency_ms, success=True)
        content = response.choices[0].message.content
        data = json.loads(content)
        return schema(**data)
    except Exception as e:
        latency_ms = int((time.time() - start) * 1000)
        _record_llm_call(agent_name, model, None, latency_ms, success=False, error_message=str(e))
        logger.exception("LLM call failed: %s", e)
        return None


def call_llm_text(system, user, temperature=0.2, max_tokens=1000, agent_name="other"):
    if not llm_available():
        return None
    model = get_model()
    start = time.time()
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        latency_ms = int((time.time() - start) * 1000)
        _record_llm_call(agent_name, model, response.usage, latency_ms, success=True)
        return response.choices[0].message.content
    except Exception as e:
        latency_ms = int((time.time() - start) * 1000)
        _record_llm_call(agent_name, model, None, latency_ms, success=False, error_message=str(e))
        logger.exception("LLM text call failed: %s", e)
        return None