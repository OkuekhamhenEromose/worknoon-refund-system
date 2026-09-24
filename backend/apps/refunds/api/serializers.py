from decimal import Decimal

from rest_framework import serializers

from apps.audit.models import AuditLog
from apps.refunds.models import RefundDecision, RefundRequest


class RefundRequestCreateSerializer(serializers.Serializer):
    customer_email = serializers.EmailField()
    order_number = serializers.CharField(max_length=40)
    order_item_id = serializers.UUIDField()
    requested_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    reason = serializers.CharField(max_length=5000, allow_blank=False, trim_whitespace=True)


class RefundDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundDecision
        fields = (
            "id",
            "outcome",
            "reason_code",
            "reason",
            "policy_result",
            "ai_result",
            "created_at",
        )


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ("id", "event_type", "message", "metadata", "created_at")


class RefundRequestSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()
    order_item = serializers.SerializerMethodField()
    decision = RefundDecisionSerializer(read_only=True)
    audit_logs = AuditLogSerializer(many=True, read_only=True)

    class Meta:
        model = RefundRequest
        fields = (
            "id",
            "customer",
            "order",
            "order_item",
            "requested_amount",
            "reason",
            "status",
            "created_at",
            "updated_at",
            "decision",
            "audit_logs",
        )

    def get_customer(self, obj):
        customer = obj.order_item.order.customer
        return {"id": str(customer.id), "name": customer.name, "email": customer.email}

    def get_order(self, obj):
        order = obj.order_item.order
        return {
            "id": str(order.id),
            "order_number": order.order_number,
            "total_amount": str(order.total_amount),
            "currency": order.currency,
            "status": order.status,
            "is_final_sale": order.is_final_sale,
            "ordered_at": order.ordered_at,
        }

    def get_order_item(self, obj):
        item = obj.order_item
        return {
            "id": str(item.id),
            "product_name": item.product_name,
            "sku": item.sku,
            "quantity": item.quantity,
            "unit_price": str(item.unit_price),
            "line_total": str(item.line_total),
            "is_damaged": item.is_damaged,
            "is_incorrect": item.is_incorrect,
        }
