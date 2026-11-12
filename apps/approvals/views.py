from rest_framework import viewsets, filters, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import ApprovalRequest
from .serializers import ApprovalRequestSerializer


class ApprovalPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ApprovalRequestViewSet(viewsets.ModelViewSet):
    queryset = ApprovalRequest.objects.select_related(
        "investigation", "decided_by"
    ).all()
    serializer_class = ApprovalRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ApprovalPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "investigation"]
    ordering_fields = ["created_at", "decided_at"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        approval = self.get_object()
        if approval.status != "pending":
            return Response({"error": "Approval is not pending."}, status=400)
        approval.status = "approved"
        approval.decided_by = request.user
        from django.utils import timezone
        approval.decided_at = timezone.now()
        approval.save()
        return Response(ApprovalRequestSerializer(approval).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        approval = self.get_object()
        if approval.status != "pending":
            return Response({"error": "Approval is not pending."}, status=400)
        approval.status = "rejected"
        approval.decided_by = request.user
        from django.utils import timezone
        approval.decided_at = timezone.now()
        approval.save()
        return Response(ApprovalRequestSerializer(approval).data)
