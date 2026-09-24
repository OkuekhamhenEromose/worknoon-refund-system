from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("refunds", "0001_initial"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="refunddecision",
            old_name="refunds_refun_outcome_9e3b36_idx",
            new_name="refunds_ref_outcome_757946_idx",
        ),
        migrations.RenameIndex(
            model_name="refunddecision",
            old_name="refunds_refun_reason_c_5d3a20_idx",
            new_name="refunds_ref_reason__a9a75e_idx",
        ),
        migrations.RenameIndex(
            model_name="refundrequest",
            old_name="refunds_refun_status_6a6a6f_idx",
            new_name="refunds_ref_status_9c10bf_idx",
        ),
        migrations.RenameIndex(
            model_name="refundrequest",
            old_name="refunds_refun_order_i_4b4b5d_idx",
            new_name="refunds_ref_order_i_15a685_idx",
        ),
    ]
