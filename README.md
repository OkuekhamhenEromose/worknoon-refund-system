# Worknoon AI-Powered Customer Support Refund System

A fully containerized full-stack assessment implementation for Worknoon's AI-powered refund challenge.

## Current status

- Phase 0 — assessment analysis: complete.
- Phase 1 — Docker/container scaffold: complete.
- Phase 2 — Django + PostgreSQL foundation: complete.
- Phase 3 — domain model: complete.
- Phase 3A — application migrations committed and aligned with the current Django migration state.
- Phase 4 — deterministic refund policy + synthetic demo data: complete.
- Phase 5 — refund REST API: complete.
- Phase 6 — AI service boundary + Gemini integration: complete.
- Phase 7 — customer refund interface: complete.
- Phase 8 — support/admin dashboard: complete.
- Phase 9 — security, edge-case tests, and health verification: complete.
- Phase 10 — final Docker/E2E verification: complete in the working environment; rerun the final verification script before submission.
- Phase 11 — final hardening: complete.
- Phase 12 — submission packaging and technical-review preparation: complete.

## Architecture

```text
Customer
   |
   v
Next.js / React / TypeScript
   |
   | HTTP/JSON
   v
Django REST Framework
   |
   +--> request validation + ownership checks
   +--> deterministic policy engine
   +--> AI analysis service (Gemini)
   +--> decision orchestrator
   +--> audit logging
   |
   v
PostgreSQL
```

The deterministic policy engine is authoritative. AI assists classification, risk detection, reasoning, and customer-facing wording; it cannot override hard policy outcomes.

## Refund policy

The implementation covers the assessment rules:

- final-sale orders are denied;
- orders older than 30 days are denied;
- refunds above $500 require human review and are escalated;
- damaged or incorrect items may qualify when the hard policy allows automatic approval;
- suspicious or conflicting requests are escalated;
- prompt-injection-like customer text is treated as untrusted input and escalated;
- if the AI provider is unavailable or returns invalid structured output, the request is escalated rather than silently approved.

Policy evaluation happens before AI. This prevents an LLM response from bypassing hard business rules.

## Domain model

```text
Customer
   |
   +--< Order
          |
          +--< OrderItem
                  |
                  +--< RefundRequest
                           |
                           +-- RefundDecision (1:1)
                           |
                           +--< AuditLog
```

## API

### Health

`GET /api/v1/health/`

Successful response:

```json
{
  "status": "ok",
  "service": "worknoon-refund-backend",
  "database": "ok"
}
```

The endpoint performs a database connectivity check and returns HTTP 503 with `database: unavailable` when the database check fails.

### Refund requests

- `GET /api/v1/refunds/requests/`
- `POST /api/v1/refunds/requests/`
- `GET /api/v1/refunds/requests/<uuid>/`

Example:

```json
{
  "customer_email": "amina.bello@example.test",
  "order_number": "WO-DEMO-001",
  "order_item_id": "<seeded-order-item-uuid>",
  "requested_amount": "120.00",
  "reason": "The item arrived as expected but I would like a refund."
}
```

The API verifies that the customer email, order number, and order item belong to the same ownership chain before processing the request.

## AI integration

The AI provider is isolated behind `apps/refunds/services/ai_service.py`.

Current provider:

- Gemini REST API using Python's standard library HTTP client.
- Configured with `AI_PROVIDER`, `AI_API_KEY`, and `AI_MODEL`.
- Customer reason is explicitly framed as untrusted data in the prompt.
- The response is expected as structured JSON and is validated before use.
- Invalid classifications/confidence values raise an AI service error.
- AI failure results in a safe `ESCALATED` decision and an `AI_FAILED` audit event.

The provider boundary keeps the orchestration layer testable without making tests depend on a live external model.

## Audit trail

The workflow records:

- `REQUEST_CREATED`
- `POLICY_EVALUATED`
- `AI_REQUESTED`
- `AI_COMPLETED`
- `AI_FAILED`
- `DECISION_CREATED`
- `REQUEST_ESCALATED`

The support dashboard exposes the decision, reason, AI classification when present, and audit trail through the API.

## Synthetic demo data

Run:

```powershell
docker compose exec backend python manage.py seed_demo_data
```

The seed command uses deterministic customer emails, order numbers, and item SKUs with `get_or_create`, so rerunning it does not create duplicate demo records.

It covers:

- eligible requests
- damaged items
- incorrect items
- final-sale requests
- old orders
- high-value requests
- suspicious prompt-injection text
- conflicting information

## Verification

From the repository root:

```powershell
Copy-Item .env.example .env
```

Set your own development values in `.env`. Never commit a real API key or secret.

Then run:

```powershell
docker compose down
docker builder prune -af
docker compose build --no-cache
docker compose up -d

docker compose exec backend python manage.py showmigrations
docker compose exec backend python manage.py makemigrations --check
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py check
docker compose exec backend pytest
docker compose exec backend python manage.py seed_demo_data
```

Expected migration state includes:

```text
audit
 [X] 0001_initial
 [X] 0002_align_django_index_names
customers
 [X] 0001_initial
orders
 [X] 0001_initial
 [X] 0002_align_django_index_names
refunds
 [X] 0001_initial
 [X] 0002_align_django_index_names
```

`makemigrations --check` should report no model changes.

Expected test result: all backend tests pass.

Open:

- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:8000/api/v1/health/`

## Demo flow

1. Open the frontend.
2. Confirm the dashboard loads seeded refund requests.
3. Select a seeded request to populate the customer/order/item fields.
4. Submit the request.
5. Show the resulting Approved/Denied/Escalated outcome.
6. Show the decision reason and AI classification where applicable.
7. Show the dashboard filters for Approved, Denied, and Escalated requests.
8. Demonstrate at least one hard-policy denial/escalation and one AI-assisted eligible request.
9. For the submission recording, show backend tests and the Docker Compose stack running.

## Security and reliability tradeoffs

- Hard business rules do not depend on the LLM.
- Customer text is untrusted input.
- Ownership is verified server-side rather than trusting identifiers independently.
- High-value refunds are escalated instead of auto-approved.
- AI failures fail safe to escalation.
- Structured AI output is validated.
- Audit events make the workflow inspectable.
- The demo uses synthetic data only.

For a production deployment, add authentication/authorization, rate limiting, secret management, HTTPS, stronger request logging/redaction, background jobs for long-running AI calls, and observability.

## Environment

Copy `.env.example` to `.env` and provide a valid AI key only if you want live Gemini analysis.

Do not commit `.env`.


## Final submission workflow

The final hardening pass adds additional API edge-case coverage, explicit AI risk-signal escalation, a reusable frontend API boundary, and a support detail view for AI response/reasoning and audit events.

Run the Windows verification helper before recording the demo:

```powershell
.\scripts\verify.ps1
```

The complete demo and technical-review checklist is in `docs/SUBMISSION_CHECKLIST.md`.

### Assessment boundary

This repository uses synthetic customer/order data only. The AI provider is an assistive component, not the source of truth for hard refund policy. Any production deployment would require authentication, authorization, rate limiting, HTTPS, managed secrets, observability, and stronger privacy controls.
