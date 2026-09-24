# Security Notes

## Implemented controls

- Environment variables are used for AI credentials.
- `.env` is ignored and excluded from the submission archive.
- Customer reason text is treated as untrusted input for the AI prompt.
- Prompt-injection-like requests are escalated by deterministic policy.
- AI structured output is validated before it influences the workflow.
- AI cannot override hard policy outcomes.
- Customer, order, and order-item ownership is verified server-side.
- Refund amounts are validated as positive decimals.
- High-value refunds are escalated for human review.
- AI provider failures fail safely to escalation.
- Audit events capture major workflow transitions.
- Synthetic data is used for the assessment.

## Important limitations

This assessment implementation is not a production authorization system. The demo endpoints do not implement a full user authentication and support-agent authorization model.

A production deployment should add:

- authentication and role-based authorization
- rate limiting and abuse controls
- HTTPS/TLS
- centralized secret management
- stricter CORS and trusted-origin configuration
- request size limits
- structured/redacted application logging
- monitoring and alerting
- asynchronous processing for long-running AI calls
- stronger tenant/data isolation if multiple organizations are supported

## Secret handling before submission

Never commit:

- `.env`
- API keys
- access tokens
- database passwords
- private certificates

If a credential has already been exposed, rotate or revoke it before submission.
