from rest_framework import viewsets, filters, permissions
from rest_framework.pagination import PageNumberPagination
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


class InvestigationStepViewSet(viewsets.ModelViewSet):
    queryset = InvestigationStep.objects.all()
    serializer_class = InvestigationStepSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["investigation", "name"]