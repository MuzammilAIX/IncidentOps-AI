from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Incident
from .serializers import IncidentSerializer


class IncidentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class IncidentViewSet(viewsets.ModelViewSet):
    """
    Full CRUD API for incidents.

    Endpoints:
      GET    /api/incidents/              â†’ list incidents (paginated)
      POST   /api/incidents/              â†’ create a new incident + trigger AI
      GET    /api/incidents/{id}/         â†’ retrieve one incident
      PUT    /api/incidents/{id}/         â†’ full update
      PATCH  /api/incidents/{id}/         â†’ partial update
      DELETE /api/incidents/{id}/         â†’ delete

    Query params:
      ?severity=high           â†’ filter by severity
      ?status=open             â†’ filter by status
      ?service=<id>            â†’ filter by service
      ?search=api              â†’ search title/description
      ?ordering=-created_at    â†’ sort
      ?page=2&page_size=20     â†’ pagination
    """
    queryset = Incident.objects.select_related("service", "created_by").all()
    serializer_class = IncidentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = IncidentPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["severity", "status", "service"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "severity", "status"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        """Save the incident. AI investigation is triggered via POST /api/incidents/{id}/investigate/."""
        incident = serializer.save()

    @action(detail=True, methods=["get"], url_path="similar", permission_classes=[AllowAny])
    def similar(self, request, pk=None):
        """Return past incidents similar to this one (same service + keyword overlap)."""
        incident = self.get_object()
        words = [w.lower() for w in incident.title.split() if len(w) > 3]

        from django.db.models import Q
        from .models import Incident as IncidentModel

        # Candidates: same service OR any keyword in title/description
        q_filter = Q(service=incident.service) if incident.service else Q()
        for w in words[:3]:
            q_filter |= Q(title__icontains=w)

        candidates = IncidentModel.objects.exclude(id=incident.id).filter(q_filter)[:20]

        results = []
        for c in candidates:
            score = 0
            if c.service_id and c.service_id == incident.service_id:
                score += 3
            for w in words:
                if w in (c.title or "").lower():
                    score += 1
                if w in (c.description or "").lower():
                    score += 1
            if score <= 0:
                continue

            investigation = c.investigations.filter(status="done").first()
            results.append({
                "id": c.id,
                "title": c.title,
                "severity": c.severity,
                "status": c.status,
                "service_name": c.service.name if c.service else "",
                "created_at": c.created_at.isoformat(),
                "root_cause": investigation.root_cause if investigation else "",
                "score": score,
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return Response({
            "incident": incident.id,
            "similar": results[:3],
        })

    @action(detail=True, methods=["post"], url_path="investigate", permission_classes=[permissions.IsAuthenticated])
    def investigate(self, request, pk=None):
        """Trigger AI investigation for this incident."""
        from apps.incidents.services import trigger_investigation
        incident = self.get_object()
        result = trigger_investigation(incident)
        return Response(result)
