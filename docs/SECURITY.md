# Security

## Foundation controls

- Environment-based settings; `.env` and secrets are ignored by Git.
- Placeholder-only example configuration.
- ORM-backed database access and a least-scope application database connection.
- Non-root runtime users in application containers.
- Generic unexpected-error responses and request correlation IDs.
- Dependency lockfiles and CI security checks.
- Server-side backend access from Next.js, avoiding permissive browser CORS defaults.

## Authentication and session controls

Authentication uses Argon2id, short-lived access tokens, hashed rotating refresh tokens, reuse detection, and backend RBAC. Access tokens stay in frontend memory; refresh tokens use an HttpOnly, SameSite cookie. Authentication attempts, logout, user administration, and alert status changes are audited without credentials or tokens.

## Required future controls

Sensitive endpoints will receive rate and body-size limits.

AI context will contain allowlisted, minimal alert data. Untrusted event text is delimited as data, never instructions. Output is schema-validated and bounded; models receive no secrets or tools and can never remediate automatically. Logs must not contain passwords, tokens, cookies, secrets, or full prompts.

Development Compose credentials are not production credentials. Production requires unique secrets, TLS, secure cookies, restricted network access, and a migration procedure.
