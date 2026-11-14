"""
LLM client — OpenAI wrapper with fallback to rule-based.
"""
import os
import json
import logging
from typing import Optional, Type, TypeVar
from pydantic import BaseModel

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


def _prepare_strict_schema(schema: dict) -> dict:
    """
    Prepare Pydantic JSON schema for OpenAI strict mode:
    1. Add 'additionalProperties': False to every object
    2. Add ALL properties to 'required' array (OpenAI demands this)
    """
    if not isinstance(schema, dict):
        return schema

    result = {}
    for key, value in schema.items():
        if key == "properties" and isinstance(value, dict):
            result[key] = {
                prop_name: _prepare_strict_schema(prop_schema)
                for prop_name, prop_schema in value.items()
            }
        elif key == "items" and isinstance(value, dict):
            result[key] = _prepare_strict_schema(value)
        elif key in ("anyOf", "oneOf", "allOf") and isinstance(value, list):
            result[key] = [_prepare_strict_schema(v) for v in value]
        elif key == "$defs" and isinstance(value, dict):
            result[key] = {
                def_name: _prepare_strict_schema(def_schema)
                for def_name, def_schema in value.items()
            }
        else:
            result[key] = value

    # If this schema is an object, enforce strict mode
    if "properties" in result:
        result["additionalProperties"] = False
        # Force ALL properties to be in 'required'
        result["required"] = list(result["properties"].keys())

    return result


def call_llm(
    system: str,
    user: str,
    schema: Type[T],
    temperature: float = 0.2,
    max_tokens: int = 2000,
) -> Optional[T]:
    if not llm_available():
        logger.info("LLM not available — skipping call")
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        raw_schema = schema.model_json_schema()
        strict_schema = _prepare_strict_schema(raw_schema)

        response = client.chat.completions.create(
            model=get_model(),
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__,
                    "strict": True,
                    "schema": strict_schema,
                },
            },
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        return schema(**data)

    except Exception as e:
        logger.exception("LLM call failed: %s", e)
        return None


def call_llm_text(
    system: str,
    user: str,
    temperature: float = 0.2,
    max_tokens: int = 1000,
) -> Optional[str]:
    if not llm_available():
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model=get_model(),
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.exception("LLM text call failed: %s", e)
        return None
