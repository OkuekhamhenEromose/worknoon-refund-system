"""Deterministic refund-policy evaluation.

The policy engine is authoritative for hard business rules. AI is intentionally
not involved here so model output cannot override a deny/escalate rule.
"""

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from typing import Literal

from django.utils import timezone

from apps.orders.models import OrderItem
from apps.refunds.models import RefundDecision


DEFAULT_MAX_REFUND_AGE_DAYS = 30
DEFAULT_AUTO_APPROVAL_LIMIT = Decimal("500.00")

PolicyOutcome = Literal["APPROVED", "DENIED", "ESCALATED"]


@dataclass(frozen=True)
class PolicyResult:
    """Immutable result returned by the deterministic policy evaluation."""

    outcome: PolicyOutcome
    reason_code: str
    reason: str
    eligible: bool
    flags: tuple[str, ...]

    def as_dict(self) -> dict:
        """Return a JSON-serializable representation for APIs and audit logs."""
        return {
            "outcome": self.outcome,
            "reason_code": self.reason_code,
            "reason": self.reason,
            "eligible": self.eligible,
            "flags": list(self.flags),
        }


def evaluate_refund_policy(
    *,
    order_item: OrderItem,
    requested_amount: Decimal,
    reason: str,
    now=None,
    max_refund_age_days: int = DEFAULT_MAX_REFUND_AGE_DAYS,
    auto_approval_limit: Decimal = DEFAULT_AUTO_APPROVAL_LIMIT,
) -> PolicyResult:
    """Evaluate refund rules in deterministic precedence order.

    Precedence:
    1. Invalid/missing request data -> escalate safely.
    2. Prompt-injection/suspicious language -> escalate.
    3. Conflicting information -> escalate.
    4. Final sale -> deny.
    5. Old order -> deny.
    6. Amount above automatic approval limit -> escalate.
    7. Damaged/incorrect item -> approve.
    8. Otherwise -> approve as policy eligible.
    """

    now = now or timezone.now()
    flags: list[str] = []

    if order_item is None or order_item.order is None:
        return PolicyResult(
            outcome="ESCALATED",
            reason_code=RefundDecision.ReasonCode.CONFLICTING_INFORMATION,
            reason="The order information required for a safe refund decision is missing.",
            eligible=False,
            flags=["missing_order_data"],
        )

    if requested_amount <= 0:
        return PolicyResult(
            outcome="ESCALATED",
            reason_code=RefundDecision.ReasonCode.CONFLICTING_INFORMATION,
            reason="The requested refund amount must be greater than zero.",
            eligible=False,
            flags=["invalid_requested_amount"],
        )

    clean_reason = (reason or "").strip()
    suspicious_phrases = (
        "ignore previous instructions",
        "ignore all previous instructions",
        "system prompt",
        "reveal your instructions",
        "bypass the policy",
        "approve regardless",
    )
    lowered_reason = clean_reason.lower()
    if any(phrase in lowered_reason for phrase in suspicious_phrases):
        flags.append("prompt_injection_signal")
        return PolicyResult(
            outcome="ESCALATED",
            reason_code=RefundDecision.ReasonCode.SUSPICIOUS_REQUEST,
            reason="The request contains instruction-like content that must be reviewed rather than treated as refund evidence.",
            eligible=False,
            flags=flags,
        )

    contradictory_pairs = (
        ("not damaged", order_item.is_damaged),
        ("undamaged", order_item.is_damaged),
        ("not incorrect", order_item.is_incorrect),
        ("correct item", order_item.is_incorrect),
    )
    if any(phrase in lowered_reason and flag for phrase, flag in contradictory_pairs):
        flags.append("conflicting_request_information")
        return PolicyResult(
            outcome="ESCALATED",
            reason_code=RefundDecision.ReasonCode.CONFLICTING_INFORMATION,
            reason="The request description conflicts with information recorded for the order item.",
            eligible=False,
            flags=flags,
        )

    order = order_item.order
    if order.is_final_sale:
        return PolicyResult(
            outcome="DENIED",
            reason_code=RefundDecision.ReasonCode.FINAL_SALE,
            reason="This order is marked as final sale and is not eligible for a refund.",
            eligible=False,
            flags=flags,
        )

    oldest_allowed = now - timedelta(days=max_refund_age_days)
    if order.ordered_at < oldest_allowed:
        return PolicyResult(
            outcome="DENIED",
            reason_code=RefundDecision.ReasonCode.ORDER_TOO_OLD,
            reason=f"The order is older than the {max_refund_age_days}-day refund window.",
            eligible=False,
            flags=flags,
        )

    if requested_amount > auto_approval_limit:
        return PolicyResult(
            outcome="ESCALATED",
            reason_code=RefundDecision.ReasonCode.ABOVE_AUTO_APPROVAL_LIMIT,
            reason=f"Refunds above {auto_approval_limit:.2f} require human review.",
            eligible=False,
            flags=flags,
        )

    if order_item.is_damaged:
        return PolicyResult(
            outcome="APPROVED",
            reason_code=RefundDecision.ReasonCode.DAMAGED_ITEM,
            reason="The item is recorded as damaged and falls within the refund policy.",
            eligible=True,
            flags=flags,
        )

    if order_item.is_incorrect:
        return PolicyResult(
            outcome="APPROVED",
            reason_code=RefundDecision.ReasonCode.INCORRECT_ITEM,
            reason="The item is recorded as incorrect and falls within the refund policy.",
            eligible=True,
            flags=flags,
        )

    return PolicyResult(
        outcome="APPROVED",
        reason_code=RefundDecision.ReasonCode.POLICY_ELIGIBLE,
        reason="The refund request satisfies the deterministic policy rules.",
        eligible=True,
        flags=flags,
    )
