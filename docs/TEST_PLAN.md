# Test Plan

## Automated coverage

The backend test suite covers the core policy, API, AI validation, health, and domain behavior.

Run:

```powershell
docker compose exec backend pytest
```

## Core scenarios

| Scenario | Expected outcome |
|---|---|
| Eligible refund | APPROVED when AI path succeeds |
| Damaged item | APPROVED when hard policy allows |
| Incorrect item | APPROVED when hard policy allows |
| Final-sale item | DENIED |
| Old order | DENIED |
| Refund above $500 | ESCALATED |
| Suspicious request | ESCALATED |
| Conflicting information | ESCALATED |
| Prompt injection | ESCALATED |
| Invalid amount | Validation error |
| Cross-customer ownership | Rejected |
| AI unavailable | ESCALATED + AI_FAILED audit |
| Invalid AI classification/confidence | AI failure path |
| Health with database | 200 + database `ok` |

## Verification gates

Before submission:

```powershell
docker compose exec backend python manage.py makemigrations --check
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py check
docker compose exec backend pytest
```

The repository should not be submitted while the test suite or migration check is failing.
