"""AI Assistant brain."""
import logging
from pydantic import BaseModel, Field
from typing import Optional
from ai_engine.llm.client import call_llm, llm_available

logger = logging.getLogger(__name__)

ASSISTANT_SYSTEM_PROMPT = """You are IncidentOps-AI Assistant, a conversational SRE co-pilot.

Your job: understand what the user wants, then take the appropriate action.

## Actions
1. create_incident — User describes a NEW problem. Params: title, severity (low/medium/high/critical), service, description.
2. search_runbooks — User asks what to do for a problem. Params: query.
3. search_incidents — User asks about history/similar problems. Params: query.
4. answer — General question. No params.

## Rules
- New problem with symptoms → create_incident
- "What should I do" → search_runbooks
- "Have we seen this before" → search_incidents
- General question → answer

Be concise. Confirm what you did."""


class AssistantAction(BaseModel):
    action: str = Field(description="create_incident, search_runbooks, search_incidents, or answer")
    title: Optional[str] = Field(None, description="For create_incident")
    severity: Optional[str] = Field(None, description="low/medium/high/critical")
    service: Optional[str] = Field(None, description="Service name")
    description: Optional[str] = Field(None, description="Incident description")
    query: Optional[str] = Field(None, description="Search query")
    response: str = Field(description="Response to show user")


def decide_action(user_message, conversation_history=None):
    if not llm_available():
        return AssistantAction(
            action="answer",
            response="LLM is not configured. Set OPENAI_API_KEY to enable the assistant.",
        )
    prompt = "User message: " + user_message
    if conversation_history:
        h = chr(10).join([m["role"] + ": " + m["content"] for m in conversation_history[-5:]])
        prompt = "Recent conversation:" + chr(10) + h + chr(10) + chr(10) + prompt
    result = call_llm(ASSISTANT_SYSTEM_PROMPT, prompt, AssistantAction, temperature=0.1, agent_name="other")
    if result is None:
        return AssistantAction(action="answer", response="I could not process that. Please try again.")
    return result
