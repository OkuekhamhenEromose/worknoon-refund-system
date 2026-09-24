# API Reference

Base URL during local development:

`http://localhost:8000/api/v1`

## Health

### `GET /health/`

Checks application and database availability.

Successful response:

```json
{
  "status": "ok",
  "service": "worknoon-refund-backend",
  "database": "ok"
}
```

Returns HTTP 503 when the database connectivity check fails.

## Refund requests

### `GET /refunds/requests/`

Returns refund requests. Optional status filtering is supported with `?status=APPROVED`, `?status=DENIED`, or `?status=ESCALATED`.

### `POST /refunds/requests/`

Creates and processes a refund request.

Example request:

```json
{
  "customer_email": "amina.bello@example.test",
  "order_number": "WO-DEMO-001",
  "order_item_id": "<seeded-order-item-uuid>",
  "requested_amount": "120.00",
  "reason": "The item arrived damaged and I would like a refund."
}
```

The backend verifies:

```text
customer email
    -> customer
    -> order belonging to customer
    -> order item belonging to order
```

The request is then evaluated by deterministic policy and, when policy-eligible, the AI service.

### `GET /refunds/requests/<uuid>/`

Returns a refund request with its decision and audit information.

## Outcome model

The final outcome is one of:

- `APPROVED`
- `DENIED`
- `ESCALATED`

Hard policy rules remain authoritative regardless of AI output.

## Audit events

Possible events include:

- `REQUEST_CREATED`
- `POLICY_EVALUATED`
- `AI_REQUESTED`
- `AI_COMPLETED`
- `AI_FAILED`
- `DECISION_CREATED`
- `REQUEST_ESCALATED`
