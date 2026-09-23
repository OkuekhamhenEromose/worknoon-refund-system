# Worknoon AI-Powered Customer Support Refund System

A deliberately small, production-minded full-stack assessment implementation for Worknoon's AI-powered refund challenge.

## Current status

- Phase 0 — assessment analysis: complete.
- Phase 1 — container contract: scaffolded.
- Phase 2 — Django + PostgreSQL foundation: implemented.
- Phase 3A — domain models: implemented in code; migration/runtime verification pending local environment.

### Verification status

Python syntax for the current backend has been checked successfully.

The current execution environment cannot install Django because outbound package access is unavailable, and it has no Docker daemon or PostgreSQL client. Therefore these runtime steps are **NOT VERIFIED here**:

- `python manage.py check`
- `python manage.py makemigrations`
- `python manage.py migrate`
- `pytest`
- PostgreSQL connectivity
- `docker compose build`
- `docker compose up`

Do not treat the migration/test/runtime gates as passed until they are executed in the local Windows environment.

## Architecture

```text
Next.js / React / TypeScript
          |
          | HTTP/JSON
          v
Django REST Framework
          |
          +--> refund orchestration
          +--> deterministic policy engine
          +--> AI analysis service
          +--> audit logging
          |
          v
      PostgreSQL
```

## Backend structure

```text
backend/
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   └── urls.py
├── apps/
│   ├── customers/
│   │   ├── apps.py
│   │   ├── models.py
│   │   └── migrations/
│   ├── orders/
│   │   ├── apps.py
│   │   ├── models.py
│   │   └── migrations/
│   ├── refunds/
│   │   ├── apps.py
│   │   ├── models.py
│   │   └── migrations/
│   └── audit/
│       ├── apps.py
│       ├── models.py
│       └── migrations/
├── manage.py
├── pytest.ini
└── tests*.py
```

## Phase 3A domain model

```text
Customer
   │
   └──< Order
          │
          └──< OrderItem
                  │
                  └──< RefundRequest
                           │
                           ├── RefundDecision (1:1)
                           │
                           └──< AuditLog
```

### Customer

Stores customer identity and contact information. UUID primary key and unique email.

### Order

Stores the customer relationship, business order number, monetary total, currency, status, final-sale flag, and order timestamp.

### OrderItem

Stores product-level refund context including quantity, unit price, SKU, damaged flag, and incorrect-item flag.

### RefundRequest

Represents the customer's refund request and its workflow status. A request is attached to an order item so the requested amount can be validated against the item value.

### RefundDecision

Stores the final application outcome (`APPROVED`, `DENIED`, or `ESCALATED`), machine-readable reason code, human-readable reason, and snapshots of policy/AI results.

### AuditLog

Stores immutable-style workflow events and structured metadata for support/admin visibility.

## Business-rule boundary

Database models enforce data integrity such as positive amounts, valid quantities, unique customer email/order numbers, and valid relationships.

The refund policy itself is intentionally **not** implemented inside model `save()` methods. The future policy engine will own rules such as:

- final-sale orders are denied;
- old orders are denied;
- refunds above the automatic approval threshold are escalated;
- damaged/incorrect items may qualify;
- suspicious or conflicting requests are escalated.

The AI layer will assist classification/reasoning but cannot override deterministic policy decisions.

## Phase 3A local verification gate

From `backend/`:

```powershell
python manage.py check
python manage.py makemigrations
python manage.py migrate
pytest
```

`makemigrations` should generate one initial migration per domain app. Inspect those files before considering the migration gate complete.

Then verify the database with:

```powershell
python manage.py showmigrations
python manage.py dbshell
```

For the Docker path, from the repository root:

```powershell
Copy-Item .env.example .env
# Set a development DJANGO_SECRET_KEY and POSTGRES_PASSWORD in .env.
docker compose build
docker compose up
```

Do not proceed to synthetic seed data until the Django migration and PostgreSQL verification gates pass.

## API foundation

`GET /api/v1/health/`

Expected response:

```json
{
  "status": "ok",
  "service": "worknoon-refund-backend"
}
```

## Next feature gate

After Phase 3A runtime verification, the next feature is synthetic data/seeding. Seed scenarios should deliberately cover eligible, final-sale, old-order, above-threshold, damaged, incorrect, suspicious, and conflicting refund cases.
