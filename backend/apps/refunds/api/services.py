from django.db import transaction

from apps.audit.models import AuditLog
from apps.orders.models import OrderItem
from apps.refunds.models import RefundRequest
from apps.refunds.services.decision_service import process_refund_request


@transaction.atomic
def create_refund_request(*, customer, order, order_item, requested_amount, reason):
    """Create and process one refund request atomically."""
    refund_request = RefundRequest.objects.create(
        order_item=order_item,
        requested_amount=requested_amount,
        reason=reason,
        status=RefundRequest.Status.PROCESSING,
    )
    AuditLog.objects.create(
        refund_request=refund_request,
        event_type=AuditLog.EventType.REQUEST_CREATED,
        message="Refund request created.",
        metadata={
            "customer_id": str(customer.id),
            "order_id": str(order.id),
            "order_item_id": str(order_item.id),
        },
    )
    return process_refund_request(refund_request)
