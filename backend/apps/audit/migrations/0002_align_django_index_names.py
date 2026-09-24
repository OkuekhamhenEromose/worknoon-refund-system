from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0001_initial"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="auditlog",
            old_name="audit_auditl_refund_r_9f95df_idx",
            new_name="audit_audit_refund__e09e21_idx",
        ),
        migrations.RenameIndex(
            model_name="auditlog",
            old_name="audit_auditl_event_t_3f8f52_idx",
            new_name="audit_audit_event_t_ac78f0_idx",
        ),
    ]
