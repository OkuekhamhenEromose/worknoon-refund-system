# Generated manually from the current domain models.
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [("customers", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("order_number", models.CharField(max_length=40, unique=True)),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ("currency", models.CharField(default="USD", max_length=3, validators=[django.core.validators.RegexValidator("^[A-Z]{3}$", "Currency must be a 3-letter uppercase ISO-style code.")])),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("PAID", "Paid"), ("SHIPPED", "Shipped"), ("DELIVERED", "Delivered"), ("CANCELLED", "Cancelled")], default="PENDING", max_length=20)),
                ("is_final_sale", models.BooleanField(default=False)),
                ("ordered_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orders", to="customers.customer")),
            ],
            options={
                "ordering": ["-ordered_at"],
                "indexes": [models.Index(fields=["customer", "-ordered_at"], name="orders_order_custome_0c6a9e_idx"), models.Index(fields=["ordered_at"], name="orders_order_ordered_2bb2e6_idx")],
                "constraints": [models.CheckConstraint(condition=models.Q(("total_amount__gte", 0)), name="order_total_amount_gte_zero")],
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("product_name", models.CharField(max_length=200)),
                ("sku", models.CharField(max_length=80)),
                ("quantity", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ("is_damaged", models.BooleanField(default=False)),
                ("is_incorrect", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="items", to="orders.order")),
            ],
            options={
                "ordering": ["created_at"],
                "indexes": [models.Index(fields=["order"], name="orders_orderi_order_id_0fcb84_idx"), models.Index(fields=["sku"], name="orders_orderi_sku_6e8c08_idx")],
                "constraints": [models.CheckConstraint(condition=models.Q(("quantity__gt", 0)), name="order_item_quantity_gt_zero"), models.CheckConstraint(condition=models.Q(("unit_price__gte", 0)), name="order_item_unit_price_gte_zero")],
            },
        ),
    ]
