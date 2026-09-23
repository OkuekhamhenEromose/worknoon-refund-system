import uuid

from django.core.validators import MinValueValidator
from django.db import models


class RefundRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        APPROVED = "APPROVED", "Approved"
        DENIED = "DENIED", "Denied"
        ESCALATED = "ESCALATED", "Escalated"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_item = models.ForeignKey(
        "orders.OrderItem",
        on_delete=models.PROTECT,
        related_name="refund_requests",
    )
    requested_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(condition=models.Q(requested_amount__gt=0), name="refund_requested_amount_gt_zero"),
        ]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["order_item", "-created_at"]),
        ]

    def __str__(self):
        return str(self.id)


class RefundDecision(models.Model):
    class Outcome(models.TextChoices):
        APPROVED = "APPROVED", "Approved"
        DENIED = "DENIED", "Denied"
        ESCALATED = "ESCALATED", "Escalated"

    class ReasonCode(models.TextChoices):
        FINAL_SALE = "FINAL_SALE", "Final sale"
        ORDER_TOO_OLD = "ORDER_TOO_OLD", "Order too old"
        ABOVE_AUTO_APPROVAL_LIMIT = "ABOVE_AUTO_APPROVAL_LIMIT", "Above auto-approval limit"
        DAMAGED_ITEM = "DAMAGED_ITEM", "Damaged item"
        INCORRECT_ITEM = "INCORRECT_ITEM", "Incorrect item"
        SUSPICIOUS_REQUEST = "SUSPICIOUS_REQUEST", "Suspicious request"
        CONFLICTING_INFORMATION = "CONFLICTING_INFORMATION", "Conflicting information"
        POLICY_ELIGIBLE = "POLICY_ELIGIBLE", "Policy eligible"
        AI_UNAVAILABLE = "AI_UNAVAILABLE", "AI unavailable"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    refund_request = models.OneToOneField(
        RefundRequest,
        on_delete=models.CASCADE,
        related_name="decision",
    )
    outcome = models.CharField(max_length=20, choices=Outcome.choices)
    reason_code = models.CharField(max_length=40, choices=ReasonCode.choices)
    reason = models.TextField()
    policy_result = models.JSONField(default=dict, blank=True)
    ai_result = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["outcome", "-created_at"]),
            models.Index(fields=["reason_code"]),
        ]

    def __str__(self):
        return f"{self.refund_request_id} - {self.outcome}"
