from rest_framework import viewsets, filters, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Investigation, InvestigationStep
from .serializers import InvestigationSerializer, InvestigationStepSerializer


class InvestigationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class InvestigationViewSet(viewsets.ModelViewSet):
    queryset = Investigation.objects.select_related("incident").prefetch_related("steps").all()
    serializer_class = InvestigationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = InvestigationPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "incident"]
    search_fields = ["root_cause"]
    ordering_fields = ["started_at", "confidence"]
    ordering = ["-started_at"]

    @action(detail=True, methods=["get"], url_path="runbooks", permission_classes=[AllowAny])
    def runbooks(self, request, pk=None):
        from ai_engine.tools.runbook_tool import search_runbooks
        inv = self.get_object()
        incident = inv.incident
        service_name = incident.service.name if incident.service else ""
        query = str(incident.title) + " " + str(incident.description or "")
        matches = search_runbooks(query=query, service_name=service_name, limit=5)
        return Response({
            "investigation": inv.id,
            "incident": incident.id,
            "incident_title": incident.title,
            "service": service_name,
            "runbooks": matches,
        })


class InvestigationStepViewSet(viewsets.ModelViewSet):
    queryset = InvestigationStep.objects.all()
    serializer_class = InvestigationStepSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["investigation", "name"]