# Architecture

## System overview

```text
Customer / Support User
        |
        v
Next.js + React + TypeScript
        |
        | HTTP / JSON
        v
Django REST Framework
        |
        +--> Request validation + ownership checks
        |
        +--> Deterministic policy engine
        |
        +--> AI service boundary (Gemini)
        |
        +--> Decision orchestrator
        |
        +--> Audit logging
        |
        v
PostgreSQL
```

## Decision flow

```text
Refund Request
      |
      v
Validate input
      |
      v
Verify customer -> order -> order item ownership
      |
      v
Deterministic policy evaluation
      |
      +---- DENIED ----------> Decision + audit
      |
      +---- ESCALATED -------> Decision + audit
      |
      +---- APPROVED-eligible
                    |
                    v
                 AI analysis
                    |
              +-----+------+
              |            |
          valid result   failure
              |            |
              v            v
         final decision  ESCALATED
              |
              v
        Decision + audit
```

## Layer responsibilities

### Frontend

Provides the customer-facing refund form and support dashboard. It does not own refund policy decisions.

### API layer

Validates request shape, resolves related records, enforces the ownership chain, and exposes refund request results.

### Policy engine

Contains deterministic business rules. It is authoritative for hard policy conditions such as final sale, order age, high-value refunds, suspicious/conflicting requests, and supported refund reasons.

### AI service

Provides classification, confidence, risk flags, reasoning, and customer-facing wording. The provider is isolated behind a small interface so tests can use mocks.

### Decision service

Orchestrates policy evaluation, AI invocation when appropriate, safe fallback behavior, persistence, and audit events.

### Persistence

PostgreSQL stores customers, orders, order items, refund requests, refund decisions, and audit logs.

## Key design decisions

1. **Policy before AI:** prevents an LLM from bypassing hard business rules.
2. **AI behind an adapter:** avoids coupling domain logic to one provider.
3. **Safe AI failure:** unavailable or malformed AI output escalates rather than approving automatically.
4. **Server-side ownership checks:** related identifiers are verified as one customer/order/item chain.
5. **Audit events:** make the decision path inspectable.
6. **Synthetic data:** keeps the assessment deterministic and avoids real customer data.

## Production extensions

For a production deployment, add authentication/authorization, rate limiting, HTTPS, stronger secret management, asynchronous AI processing where needed, structured observability, and more granular support-agent permissions.
