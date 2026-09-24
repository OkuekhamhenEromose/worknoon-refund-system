from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="order",
            old_name="orders_order_custome_0c6a9e_idx",
            new_name="orders_orde_custome_6c4b7b_idx",
        ),
        migrations.RenameIndex(
            model_name="order",
            old_name="orders_order_ordered_2bb2e6_idx",
            new_name="orders_orde_ordered_30150d_idx",
        ),
        migrations.RenameIndex(
            model_name="orderitem",
            old_name="orders_orderi_order_id_0fcb84_idx",
            new_name="orders_orde_order_i_5d347b_idx",
        ),
        migrations.RenameIndex(
            model_name="orderitem",
            old_name="orders_orderi_sku_6e8c08_idx",
            new_name="orders_orde_sku_737ca0_idx",
        ),
    ]
