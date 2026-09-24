# Generated manually from the current domain models.
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [("refunds", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("event_type", models.CharField(choices=[("REQUEST_CREATED", "Request created"), ("POLICY_EVALUATED", "Policy evaluated"), ("AI_REQUESTED", "AI requested"), ("AI_COMPLETED", "AI completed"), ("AI_FAILED", "AI failed"), ("DECISION_CREATED", "Decision created"), ("REQUEST_ESCALATED", "Request escalated")], max_length=40)),
                ("message", models.TextField()),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("refund_request", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="audit_logs", to="refunds.refundrequest")),
            ],
            options={
                "ordering": ["created_at"],
                "indexes": [models.Index(fields=["refund_request", "created_at"], name="audit_auditl_refund_r_9f95df_idx"), models.Index(fields=["event_type", "created_at"], name="audit_auditl_event_t_3f8f52_idx")],
            },
        ),
    ]
