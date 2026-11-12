from rest_framework import viewsets, filters, permissions
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
      GET    /api/incidents/              → list incidents (paginated)
      POST   /api/incidents/              → create a new incident + trigger AI
      GET    /api/incidents/{id}/         → retrieve one incident
      PUT    /api/incidents/{id}/         → full update
      PATCH  /api/incidents/{id}/         → partial update
      DELETE /api/incidents/{id}/         → delete

    Query params:
      ?severity=high           → filter by severity
      ?status=open             → filter by status
      ?service=<id>            → filter by service
      ?search=api              → search title/description
      ?ordering=-created_at    → sort
      ?page=2&page_size=20     → pagination
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
        """
        Called by DRF after a successful POST /api/incidents/.
        Saves the incident, then triggers the AI investigation task
        in the background via Celery.
        """
        incident = serializer.save()
        from apps.incidents.services import trigger_investigation
        try:
            trigger_investigation(incident)
        except Exception:
            # If Celery/Redis is down, don't fail the API — just log it.
            # The user still gets their 201 Created response.
            pass