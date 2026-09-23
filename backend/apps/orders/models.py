import uuid

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="orders",
    )
    order_number = models.CharField(max_length=40, unique=True)
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
        validators=[RegexValidator(r"^[A-Z]{3}$", "Currency must be a 3-letter uppercase ISO-style code.")],
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    is_final_sale = models.BooleanField(default=False)
    ordered_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-ordered_at"]
        constraints = [
            models.CheckConstraint(condition=models.Q(total_amount__gte=0), name="order_total_amount_gte_zero"),
        ]
        indexes = [
            models.Index(fields=["customer", "-ordered_at"]),
            models.Index(fields=["ordered_at"]),
        ]

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="items",
    )
    product_name = models.CharField(max_length=200)
    sku = models.CharField(max_length=80)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    is_damaged = models.BooleanField(default=False)
    is_incorrect = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gt=0), name="order_item_quantity_gt_zero"),
            models.CheckConstraint(condition=models.Q(unit_price__gte=0), name="order_item_unit_price_gte_zero"),
        ]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["sku"]),
        ]

    @property
    def line_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.order.order_number} - {self.product_name}"
