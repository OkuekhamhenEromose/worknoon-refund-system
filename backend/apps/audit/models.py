import uuid

from django.db import models


class AuditLog(models.Model):
    class EventType(models.TextChoices):
        REQUEST_CREATED = "REQUEST_CREATED", "Request created"
        POLICY_EVALUATED = "POLICY_EVALUATED", "Policy evaluated"
        AI_REQUESTED = "AI_REQUESTED", "AI requested"
        AI_COMPLETED = "AI_COMPLETED", "AI completed"
        AI_FAILED = "AI_FAILED", "AI failed"
        DECISION_CREATED = "DECISION_CREATED", "Decision created"
        REQUEST_ESCALATED = "REQUEST_ESCALATED", "Request escalated"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    refund_request = models.ForeignKey(
        "refunds.RefundRequest",
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )
    event_type = models.CharField(max_length=40, choices=EventType.choices)
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["refund_request", "created_at"]),
            models.Index(fields=["event_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.refund_request_id}"
