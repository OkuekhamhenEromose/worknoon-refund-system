# Generated manually from the current domain models.
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [("orders", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="RefundRequest",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("requested_amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0.01)])),
                ("reason", models.TextField()),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("PROCESSING", "Processing"), ("APPROVED", "Approved"), ("DENIED", "Denied"), ("ESCALATED", "Escalated")], default="PENDING", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order_item", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="refund_requests", to="orders.orderitem")),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [models.Index(fields=["status", "-created_at"], name="refunds_refun_status_6a6a6f_idx"), models.Index(fields=["order_item", "-created_at"], name="refunds_refun_order_i_4b4b5d_idx")],
                "constraints": [models.CheckConstraint(condition=models.Q(("requested_amount__gt", 0)), name="refund_requested_amount_gt_zero")],
            },
        ),
        migrations.CreateModel(
            name="RefundDecision",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("outcome", models.CharField(choices=[("APPROVED", "Approved"), ("DENIED", "Denied"), ("ESCALATED", "Escalated")], max_length=20)),
                ("reason_code", models.CharField(choices=[("FINAL_SALE", "Final sale"), ("ORDER_TOO_OLD", "Order too old"), ("ABOVE_AUTO_APPROVAL_LIMIT", "Above auto-approval limit"), ("DAMAGED_ITEM", "Damaged item"), ("INCORRECT_ITEM", "Incorrect item"), ("SUSPICIOUS_REQUEST", "Suspicious request"), ("CONFLICTING_INFORMATION", "Conflicting information"), ("POLICY_ELIGIBLE", "Policy eligible"), ("AI_UNAVAILABLE", "AI unavailable")], max_length=40)),
                ("reason", models.TextField()),
                ("policy_result", models.JSONField(blank=True, default=dict)),
                ("ai_result", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("refund_request", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="decision", to="refunds.refundrequest")),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [models.Index(fields=["outcome", "-created_at"], name="refunds_refun_outcome_9e3b36_idx"), models.Index(fields=["reason_code"], name="refunds_refun_reason_c_5d3a20_idx")],
            },
        ),
    ]
