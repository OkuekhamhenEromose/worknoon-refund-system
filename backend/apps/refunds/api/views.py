from django.db.models import Prefetch
from rest_framework import generics, status
from rest_framework.response import Response

from apps.audit.models import AuditLog
from apps.customers.models import Customer
from apps.orders.models import Order, OrderItem
from apps.refunds.api.serializers import RefundRequestCreateSerializer, RefundRequestSerializer
from apps.refunds.api.services import create_refund_request
from apps.refunds.models import RefundRequest


class RefundRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = RefundRequestSerializer

    def get_queryset(self):
        queryset = (
            RefundRequest.objects.select_related(
                "order_item__order__customer",
            )
            .prefetch_related(
                "decision",
                Prefetch("audit_logs", queryset=AuditLog.objects.order_by("created_at")),
            )
        )
        request_status = self.request.query_params.get("status")
        if request_status:
            queryset = queryset.filter(status=request_status.upper())
        return queryset

    def create(self, request, *args, **kwargs):
        input_serializer = RefundRequestCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        try:
            customer = Customer.objects.get(email__iexact=data["customer_email"])
        except Customer.DoesNotExist:
            return Response(
                {"detail": "Customer was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            order = Order.objects.get(order_number=data["order_number"], customer=customer)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order was not found for this customer."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            order_item = OrderItem.objects.get(id=data["order_item_id"], order=order)
        except OrderItem.DoesNotExist:
            return Response(
                {"detail": "Order item was not found on this order."},
                status=status.HTTP_404_NOT_FOUND,
            )

        refund_request = create_refund_request(
            customer=customer,
            order=order,
            order_item=order_item,
            requested_amount=data["requested_amount"],
            reason=data["reason"],
        )

        refund_request = self.get_queryset().get(pk=refund_request.pk)
        return Response(
            RefundRequestSerializer(refund_request).data,
            status=status.HTTP_201_CREATED,
        )


class RefundRequestDetailView(generics.RetrieveAPIView):
    serializer_class = RefundRequestSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return (
            RefundRequest.objects.select_related("order_item__order__customer")
            .prefetch_related(
                "decision",
                Prefetch("audit_logs", queryset=AuditLog.objects.order_by("created_at")),
            )
        )
