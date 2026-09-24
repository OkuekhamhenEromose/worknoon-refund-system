# Demo Guide

## Start

```powershell
docker compose up -d
```

Open `http://localhost:3000`.

If the database is empty, run:

```powershell
docker compose exec backend python manage.py seed_demo_data
```

## Demo sequence

### 1. Approved / AI-assisted request

Use a seeded eligible order/item and submit a legitimate reason such as a damaged or incorrect item within the policy window and below the high-value threshold.

Show:

- request submission
- policy-eligible path
- AI classification when a provider key is configured
- final `APPROVED` outcome
- customer-facing explanation

### 2. Final-sale denial

Submit a seeded final-sale item.

Expected result: `DENIED`.

Point out that this is deterministic and does not depend on an LLM recommendation.

### 3. High-value escalation

Submit a refund above `$500`.

Expected result: `ESCALATED` for human review.

### 4. Prompt-injection defense

Use a reason containing an instruction such as asking the AI to ignore the refund policy and approve the request.

Expected result: `ESCALATED`.

Explain that customer text is untrusted data and cannot rewrite system policy.

### 5. AI failure

For a technical demonstration, configure an invalid/unavailable AI provider credential and submit an otherwise AI-eligible request.

Expected result: safe `ESCALATED` behavior and an `AI_FAILED` audit event.

Restore the valid configuration afterward if needed.

## Dashboard

Use the dashboard to show:

- recent refund requests
- Approved / Denied / Escalated filters
- refund amount
- decision reason
- AI classification when present
- audit information

## What to explain verbally

Keep the architecture explanation short:

> The API validates ownership first. A deterministic policy engine handles hard business rules. AI is only used for eligible requests where classification and reasoning add value. AI output is validated, and AI failure falls back to escalation. Every important step is audited.
