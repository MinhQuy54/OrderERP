from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .models import Order
from .serializers import OrderSerializer, RevenueReportSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status"]
    search_fields = ["customer", "item"]
    ordering_fields = ["created_at", "amount", "qty"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as exc:
            raise DRFValidationError(detail=exc.message_dict if hasattr(exc, "message_dict") else exc.messages)

    def perform_update(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as exc:
            raise DRFValidationError(detail=exc.message_dict if hasattr(exc, "message_dict") else exc.messages)

    @action(detail=False, methods=["get"], url_path="revenue-report")
    def revenue_report(self, request):
        daily_data = (
            Order.objects.filter(status=Order.Status.DA_GIAO)
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(
                total_orders=Count("id"),
                total_revenue=Sum("amount"),
            )
            .order_by("-date")
        )

        overall = Order.objects.filter(status=Order.Status.DA_GIAO).aggregate(
            total_delivered_orders=Count("id"),
            total_revenue=Sum("amount"),
        )
        overall["total_revenue"] = overall["total_revenue"] or 0
        overall["total_delivered_orders"] = overall["total_delivered_orders"] or 0

        serializer = RevenueReportSerializer(daily_data, many=True)

        return Response(
            {
                "summary": overall,
                "daily_report": serializer.data,
            }
        )
