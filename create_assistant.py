"""Create assistant app with all backend files."""
import os

base = '/app/apps/assistant'
os.makedirs(base + '/migrations', exist_ok=True)

files = {}

# __init__.py
files[base + '/__init__.py'] = ''

# migrations/__init__.py
files[base + '/migrations/__init__.py'] = ''

# apps.py
files[base + '/apps.py'] = '''from django.apps import AppConfig


class AssistantConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.assistant"
    verbose_name = "AI Assistant"
'''

# models.py
files[base + '/models.py'] = '''"""AI Assistant conversation models."""
from django.db import models
from django.conf import settings


class Conversation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assistant_conversations",
    )
    title = models.CharField(max_length=200, default="New conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation<{self.id}> by {self.user.username}"


class Message(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.TextField()
    action_taken = models.CharField(max_length=32, blank=True)
    action_result = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
'''

# tools.py
files[base + '/tools.py'] = '''"""Tools available to the AI assistant."""
from apps.incidents.models import Incident
from apps.services.models import Service
from ai_engine.tools.runbook_tool import search_runbooks as search_runbooks_impl
from apps.incidents.services import trigger_investigation


def create_incident(title, severity="high", service="", description=""):
    if severity not in ("low", "medium", "high", "critical"):
        severity = "high"
    svc = None
    if service:
        svc = Service.objects.filter(name=service).first()
    incident = Incident.objects.create(
        title=title[:255], description=description or title,
        severity=severity, status="open", service=svc,
    )
    result = {"incident_id": incident.id, "title": incident.title, "severity": severity}
    try:
        qr = trigger_investigation(incident)
        result["investigation_queued"] = qr.get("queued", False)
        result["task_id"] = qr.get("task_id")
    except Exception as e:
        result["investigation_error"] = str(e)
    return result


def search_runbooks_tool(query, limit=3):
    matches = search_runbooks_impl(query=query, service_name="", limit=limit)
    return {
        "count": len(matches),
        "runbooks": [
            {"code": r["code"], "title": r["title"], "category": r["category"], "score": r["score"]}
            for r in matches
        ],
    }


def search_incidents_tool(query, limit=5):
    qs = Incident.objects.all()
    if query:
        words = [w for w in query.lower().split() if len(w) > 3][:3]
        from django.db.models import Q
        q = Q()
        for w in words:
            q |= Q(title__icontains=w) | Q(description__icontains=w)
        qs = qs.filter(q) if q else qs
    incidents = qs.order_by("-created_at")[:limit]
    return {
        "count": incidents.count(),
        "incidents": [
            {
                "id": i.id, "title": i.title, "severity": i.severity,
                "status": i.status, "service": i.service.name if i.service else "",
                "created_at": i.created_at.isoformat(),
            }
            for i in incidents
        ],
    }


def answer_question(question):
    return {"answered": True, "question": question}
'''

# llm.py
files[base + '/llm.py'] = '''"""AI Assistant brain."""
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
'''

# serializers.py
files[base + '/serializers.py'] = '''"""Assistant API serializers."""
from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "role", "content", "action_taken", "action_result", "created_at"]
        read_only_fields = ["id", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.IntegerField(source="messages.count", read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "title", "messages", "message_count", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
'''

# views.py
files[base + '/views.py'] = '''"""Assistant API views."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .llm import decide_action
from .tools import create_incident as tool_create_incident, search_runbooks_tool, search_incidents_tool, answer_question


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="send")
    def send(self, request, pk=None):
        conversation = self.get_object()
        user_message = request.data.get("message", "").strip()
        if not user_message:
            return Response({"error": "message required"}, status=status.HTTP_400_BAD_REQUEST)

        Message.objects.create(conversation=conversation, role="user", content=user_message)

        history = [{"role": m.role, "content": m.content} for m in conversation.messages.all()[:20]]

        decision = decide_action(user_message, history)

        action_result = {}
        try:
            if decision.action == "create_incident":
                action_result = tool_create_incident(
                    title=decision.title or user_message,
                    severity=decision.severity or "high",
                    service=decision.service or "",
                    description=decision.description or user_message,
                )
            elif decision.action == "search_runbooks":
                action_result = search_runbooks_tool(query=decision.query or user_message)
            elif decision.action == "search_incidents":
                action_result = search_incidents_tool(query=decision.query or user_message)
            else:
                action_result = answer_question(question=user_message)
        except Exception as e:
            action_result = {"error": str(e)}

        assistant_message = Message.objects.create(
            conversation=conversation, role="assistant",
            content=decision.response or "(no response)",
            action_taken=decision.action, action_result=action_result,
        )
        conversation.save()

        return Response({
            "user_message": user_message,
            "assistant_message": MessageSerializer(assistant_message).data,
            "action": decision.action,
            "result": action_result,
        }, status=status.HTTP_201_CREATED)
'''

# urls.py
files[base + '/urls.py'] = '''from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet

router = DefaultRouter()
router.register(r"", ConversationViewSet, basename="conversation")

urlpatterns = router.urls
'''

for path, content in files.items():
    with open(path, 'w') as f:
        f.write(content)
    print('Created:', path)

print('\\nAll files created')
