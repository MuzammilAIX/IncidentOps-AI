"""Assistant API views."""
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
