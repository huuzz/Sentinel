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

Sensitive endpoints now have rate limits and streamed body-size limits. See [HARDENING.md](HARDENING.md)
for quotas, production settings, proxy trust, security headers, scanner workflows, and limitations.

AI context will contain allowlisted, minimal alert data. Untrusted event text is delimited as data, never instructions. Output is schema-validated and bounded; models receive no secrets or tools and can never remediate automatically. Logs must not contain passwords, tokens, cookies, secrets, or full prompts.

The Milestone 3 analyzer receives only alert fields and explicitly selected evidence attributes; event
metadata is excluded. Returned evidence IDs must belong to the analyzed alert. The local fake provider
is deterministic and does not make network calls. Analyses are advisory, never trigger tools or
remediation, and store only user-facing output—not prompts or chain-of-thought.

Development Compose credentials are not production credentials. Production requires unique secrets, TLS, secure cookies, restricted network access, and a migration procedure.

## ML artifact safety

Only the repository-owned, checksum-verified joblib artifact is loaded. Feature-schema mismatches,
missing files, and checksum failures leave ML unavailable without blocking event ingestion. Never load
user-supplied serialized models. Anomaly scores are advisory and must not be described as attack
probabilities or autonomous alert decisions.

## Grounded knowledge safety

Only administrators ingest sources, and each entry must be classified as authored, public, or
user-authorized. Questions, documents, and retrieved excerpts are bounded untrusted data. Retrieval
returns at most five attributed chunks. The local generator receives no tools or secrets, performs no
actions, and stores no hidden reasoning. Users must verify cited material before acting.
