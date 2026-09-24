# Worknoon Submission Checklist

Use this checklist immediately before submitting the assessment.

## 1. Repository hygiene

- [ ] Repository contains source code, not a ZIP inside the repository.
- [ ] `.env` is not committed.
- [ ] No API keys, passwords, tokens, or private credentials appear in tracked files.
- [ ] `.env.example` documents required configuration without real secrets.
- [ ] `__pycache__`, `.pytest_cache`, `.next`, `node_modules`, and local build artifacts are excluded.
- [ ] Git status has no accidental files.

Recommended checks:

```powershell
git status
git ls-files | Select-String "\.env$"
git grep -n -I -E "AIza|sk-[A-Za-z0-9]|api[_-]?key\s*=" -- . ':!package-lock.json'
```

If a real credential was ever exposed, rotate/revoke it before submission.

## 2. Clean Docker verification

From the repository root:

```powershell
docker compose down
docker builder prune -af
docker compose build --no-cache
docker compose up -d
docker compose ps
```

Expected services:

- PostgreSQL: healthy
- Backend: running
- Frontend: running

## 3. Backend verification

```powershell
docker compose exec backend python manage.py showmigrations
docker compose exec backend python manage.py makemigrations --check
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py check
docker compose exec backend pytest
docker compose exec backend python manage.py seed_demo_data
```

Required gates:

- [ ] All application migrations are marked `[X]`.
- [ ] `makemigrations --check` reports no model changes.
- [ ] `migrate` reports no pending migrations.
- [ ] Django system check has no issues.
- [ ] Full pytest suite passes.
- [ ] Seed command completes without errors.

## 4. API verification

Health endpoint:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health/
```

Expected shape:

```json
{
  "status": "ok",
  "service": "worknoon-refund-backend",
  "database": "ok"
}
```

- [ ] Health endpoint returns HTTP 200.
- [ ] Database status is `ok`.
- [ ] Refund request list/detail endpoints respond.
- [ ] A valid refund request can be processed.
- [ ] Final-sale request is denied by deterministic policy.
- [ ] Refund above $500 is escalated.
- [ ] Prompt-injection-like input is escalated.
- [ ] AI failure is handled safely as escalation.
- [ ] Cross-customer ownership cannot be bypassed.

## 5. Frontend verification

Open:

- `http://localhost:3000`
- `http://localhost:8000/api/v1/health/`

- [ ] Customer refund form loads.
- [ ] Seeded request data can populate the form.
- [ ] Submit/loading/error states work.
- [ ] Final decision is visible.
- [ ] Decision reason is visible.
- [ ] AI classification is visible when available.
- [ ] Dashboard loads recent requests.
- [ ] Approved/Denied/Escalated filters work.
- [ ] Layout is usable at desktop and narrow widths.

## 6. AI verification

- [ ] `AI_PROVIDER`, `AI_API_KEY`, and `AI_MODEL` are documented.
- [ ] Live AI calls are optional for deterministic policy tests.
- [ ] Customer text is treated as untrusted input.
- [ ] AI output is schema/field validated.
- [ ] AI cannot override hard policy decisions.
- [ ] AI unavailable/malformed responses fail safely to escalation.

For a recording, demonstrate both an AI-assisted eligible request and a deterministic hard-policy outcome.

## 7. Demo recording

Recommended 4–6 minute flow:

1. Show repository and README briefly.
2. Run `docker compose up -d` or show the already-running stack.
3. Open the customer refund interface.
4. Submit a normal eligible request.
5. Show the returned decision and explanation.
6. Show an example denied by final-sale policy.
7. Show an example escalated because the amount exceeds $500.
8. Show a prompt-injection attempt being escalated.
9. Open the support dashboard.
10. Show filters, decision reasons, AI classification, and audit information.
11. Briefly explain that deterministic policy is authoritative and AI is an assisting layer.
12. Show the passing backend test command/result.

## 8. GitHub submission

- [ ] Repository is public if the assessment requires a public repository.
- [ ] Repository root contains `README.md` and `docker-compose.yml`.
- [ ] `docs/` contains the supporting assessment documents.
- [ ] Setup works from a clean clone using documented steps.
- [ ] Commit history is professional enough to review.
- [ ] README contains architecture, policy, AI, security, setup, testing, tradeoffs, and demo instructions.
- [ ] Video link is ready.
- [ ] Final repository URL is ready.

## 9. Final reviewer questions

Before submitting, be able to answer:

- Why is deterministic policy evaluated before AI?
- What can the AI change, and what can it never change?
- How is prompt injection handled?
- What happens when Gemini is unavailable?
- How is customer/order ownership validated?
- How are decisions audited?
- Why are refunds above $500 escalated?
- What would you add for production authentication/authorization?
- What are the main trade-offs of this implementation?

## 10. Final submission package

Submit only what the assessment asks for:

- Public GitHub repository URL
- Short demo video/link
- Any required written response

Do not submit `.env` or real credentials.
