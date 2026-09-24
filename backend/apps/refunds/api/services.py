from django.db import transaction

from apps.audit.models import AuditLog
from apps.orders.models import OrderItem
from apps.refunds.models import RefundDecision, RefundRequest
from apps.refunds.services.policy_engine import evaluate_refund_policy


@transaction.atomic
def create_refund_request(*, customer, order, order_item, requested_amount, reason):
    """Create, evaluate, decide, and audit one refund request atomically."""
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

    policy_result = evaluate_refund_policy(
        order_item=order_item,
        requested_amount=requested_amount,
        reason=reason,
    )

    AuditLog.objects.create(
        refund_request=refund_request,
        event_type=AuditLog.EventType.POLICY_EVALUATED,
        message=policy_result.reason,
        metadata=policy_result.as_dict(),
    )

    decision = RefundDecision.objects.create(
        refund_request=refund_request,
        outcome=policy_result.outcome,
        reason_code=policy_result.reason_code,
        reason=policy_result.reason,
        policy_result=policy_result.as_dict(),
        ai_result={},
    )

    refund_request.status = policy_result.outcome
    refund_request.save(update_fields=["status", "updated_at"])

    AuditLog.objects.create(
        refund_request=refund_request,
        event_type=AuditLog.EventType.DECISION_CREATED,
        message=f"Refund decision created: {decision.outcome}.",
        metadata={
            "decision_id": str(decision.id),
            "outcome": decision.outcome,
            "reason_code": decision.reason_code,
        },
    )

    if decision.outcome == RefundDecision.Outcome.ESCALATED:
        AuditLog.objects.create(
            refund_request=refund_request,
            event_type=AuditLog.EventType.REQUEST_ESCALATED,
            message="Refund request requires human review.",
            metadata={"reason_code": decision.reason_code},
        )

    return refund_request
