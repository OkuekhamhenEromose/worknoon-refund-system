from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.customers.models import Customer
from apps.orders.models import Order, OrderItem
from apps.refunds.models import RefundDecision, RefundRequest
from apps.audit.models import AuditLog


@pytest.mark.django_db
def test_domain_relationships_and_constraints():
    customer = Customer.objects.create(name="Ada Example", email="ada@example.com")
    order = Order.objects.create(
        customer=customer,
        order_number="WO-1001",
        total_amount=Decimal("150.00"),
        ordered_at=timezone.now() - timedelta(days=2),
        status=Order.Status.DELIVERED,
    )
    item = OrderItem.objects.create(
        order=order,
        product_name="Headphones",
        sku="HP-001",
        quantity=1,
        unit_price=Decimal("150.00"),
        is_damaged=True,
    )
    request = RefundRequest.objects.create(
        order_item=item,
        requested_amount=Decimal("150.00"),
        reason="The item arrived damaged.",
    )
    decision = RefundDecision.objects.create(
        refund_request=request,
        outcome=RefundDecision.Outcome.APPROVED,
        reason_code=RefundDecision.ReasonCode.DAMAGED_ITEM,
        reason="The damaged item qualifies for refund review.",
        policy_result={"eligible": True},
        ai_result={"classification": "damaged_item"},
    )
    log = AuditLog.objects.create(
        refund_request=request,
        event_type=AuditLog.EventType.DECISION_CREATED,
        message="Refund decision created.",
    )

    assert customer.orders.get() == order
    assert order.items.get() == item
    assert item.refund_requests.get() == request
    assert request.decision == decision
    assert list(request.audit_logs.all()) == [log]
    assert item.line_total == Decimal("150.00")
