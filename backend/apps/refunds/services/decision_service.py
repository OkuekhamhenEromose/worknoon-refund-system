"""Application orchestration for deterministic policy + AI analysis."""

from __future__ import annotations

from apps.audit.models import AuditLog
from apps.refunds.models import RefundDecision, RefundRequest
from apps.refunds.services.ai_service import AIServiceError, analyze_refund_request
from apps.refunds.services.policy_engine import PolicyResult, evaluate_refund_policy


def _order_context(refund_request: RefundRequest) -> dict:
    item = refund_request.order_item
    order = item.order
    return {
        "order_number": order.order_number,
        "total_amount": str(order.total_amount),
        "currency": order.currency,
        "status": order.status,
        "is_final_sale": order.is_final_sale,
        "ordered_at": order.ordered_at.isoformat(),
        "item": {
            "product_name": item.product_name,
            "sku": item.sku,
            "quantity": item.quantity,
            "unit_price": str(item.unit_price),
            "is_damaged": item.is_damaged,
            "is_incorrect": item.is_incorrect,
        },
    }


def process_refund_request(refund_request: RefundRequest) -> RefundRequest:
    """Run policy, AI analysis where appropriate, then persist one final decision."""
    item = refund_request.order_item
    policy_result = evaluate_refund_policy(
        order_item=item,
        requested_amount=refund_request.requested_amount,
        reason=refund_request.reason,
    )
    AuditLog.objects.create(
        refund_request=refund_request,
        event_type=AuditLog.EventType.POLICY_EVALUATED,
        message=policy_result.reason,
        metadata=policy_result.as_dict(),
    )

    # Hard policy denies/escalations remain authoritative and do not need an AI
    # call merely to re-decide the outcome.
    ai_result = None
    if policy_result.outcome == "APPROVED":
        AuditLog.objects.create(
            refund_request=refund_request,
            event_type=AuditLog.EventType.AI_REQUESTED,
            message="AI analysis requested for an otherwise policy-eligible refund.",
            metadata={"provider": "configured"},
        )
        try:
            ai_result = analyze_refund_request(
                reason=refund_request.reason,
                order_context=_order_context(refund_request),
                policy_context=policy_result.as_dict(),
            )
            AuditLog.objects.create(
                refund_request=refund_request,
                event_type=AuditLog.EventType.AI_COMPLETED,
                message="AI analysis completed and validated.",
                metadata=ai_result.as_dict(),
            )
        except AIServiceError as exc:
            AuditLog.objects.create(
                refund_request=refund_request,
                event_type=AuditLog.EventType.AI_FAILED,
                message="AI analysis failed; request moved to human review.",
                metadata={"error": str(exc)},
            )
            policy_result = PolicyResult(
                outcome="ESCALATED",
                reason_code=RefundDecision.ReasonCode.AI_UNAVAILABLE,
                reason="The refund satisfies the deterministic policy, but AI analysis is unavailable. Human review is required.",
                eligible=False,
                flags=(*policy_result.flags, "ai_unavailable"),
            )
        else:
            # AI can surface additional risk signals, but it still cannot
            # approve a request that the application should send to review.
            risk_values = {flag.strip().lower() for flag in ai_result.risk_flags}
            suspicious_signal = (
                ai_result.classification == "SUSPICIOUS_REQUEST"
                or "prompt_injection" in risk_values
                or "prompt_injection_attempt" in risk_values
                or "suspicious_request" in risk_values
            )
            conflicting_signal = (
                ai_result.classification == "CONFLICTING_INFORMATION"
                or "conflicting_information" in risk_values
            )
            if suspicious_signal or conflicting_signal:
                reason_code = (
                    RefundDecision.ReasonCode.SUSPICIOUS_REQUEST
                    if suspicious_signal
                    else RefundDecision.ReasonCode.CONFLICTING_INFORMATION
                )
                policy_result = PolicyResult(
                    outcome="ESCALATED",
                    reason_code=reason_code,
                    reason="AI analysis identified a risk signal that requires human review.",
                    eligible=False,
                    flags=(
                        *policy_result.flags,
                        "ai_risk_signal",
                    ),
                )

    decision = RefundDecision.objects.create(
        refund_request=refund_request,
        outcome=policy_result.outcome,
        reason_code=policy_result.reason_code,
        reason=policy_result.reason,
        policy_result=policy_result.as_dict(),
        ai_result=ai_result.as_dict() if ai_result else {},
    )
    refund_request.status = policy_result.outcome
    refund_request.save(update_fields=["status", "updated_at"])
    AuditLog.objects.create(
        refund_request=refund_request,
        event_type=AuditLog.EventType.DECISION_CREATED,
        message=f"Refund decision created: {decision.outcome}.",
        metadata={"decision_id": str(decision.id), "outcome": decision.outcome, "reason_code": decision.reason_code},
    )
    if decision.outcome == RefundDecision.Outcome.ESCALATED:
        AuditLog.objects.create(
            refund_request=refund_request,
            event_type=AuditLog.EventType.REQUEST_ESCALATED,
            message="Refund request requires human review.",
            metadata={"reason_code": decision.reason_code},
        )
    return refund_request
