# Security hardening

This remains an educational local deployment, not a production-security certification.

## Request controls

Backend and Next.js proxy bodies are capped at 1 MiB while streaming. Backend limits are configurable;
the browser proxy intentionally retains a fixed 1 MiB ceiling. Oversized requests return 413.
Rate limits apply per client address and category over a rolling 60-second window:

| Category | Default requests | Routes |
|---|---:|---|
| Authentication | 10 | Login and refresh |
| Ingestion | 120 | Event creation |
| Advisory AI/RAG | 10 | Alert analysis and knowledge questions |
| Administration | 30 | User writes and knowledge ingestion |

429 responses include `Retry-After`. The limiter is process-local, bounded to 10,000 address/category
keys, and resets on restart. It is intended for one backend process; multiple workers/replicas need a
shared gateway limiter before deployment. Requests through the Next.js proxy share its address and
therefore its quota by default. Rate limiting supplements, never replaces, RBAC.

Forwarded headers are ignored by default. Uvicorn proxy-header handling is disabled in Docker.
`SENTINEL_TRUSTED_PROXY_IPS` accepts explicit proxy peers; a trusted proxy must overwrite
`X-Forwarded-For` with one validated address. Wildcard proxy trust is rejected. Do not expose the
backend around the configured gateway in production.

## Production configuration

Set `SENTINEL_ENVIRONMENT=production`, a unique random JWT secret, secure refresh cookies, and explicit
HTTPS CORS origins when cross-origin browser access is actually required. Unsafe production defaults
are rejected on startup. The default same-origin proxy needs no CORS allowlist. TLS termination,
network restrictions, database least privilege, backups, and a reviewed deployment configuration
remain prerequisites. Compose is development-only; it does not provision TLS or cloud resources.

Responses set anti-framing, MIME-sniffing, referrer, and permissions headers. The backend adds a
restrictive CSP to API responses; documentation routes retain their required scripts. Production
backend responses include HSTS. Configure HSTS on the public TLS frontend/gateway too.
Application containers run non-root with all Linux capabilities dropped and no-new-privileges.

## Supply chain and verification

CI validates migrations against an empty pgvector database and checks schema drift. Security workflows
run dependency review, Gitleaks, CodeQL, filesystem and container vulnerability scans, and generate an
SPDX SBOM artifact. New scanner actions are pinned to resolved commit hashes; Dependabot monitors
actions and package dependencies. Scan findings must be reviewed, not silently suppressed.

The Trivy pin uses the verified [v0.36.0 release](https://github.com/aquasecurity/trivy-action/releases/tag/v0.36.0).
The SBOM workflow uses [Anchore's SBOM action](https://github.com/anchore/sbom-action).
Hosted scan success depends on repository permissions and current vulnerability databases; local
unit/build success does not imply a clean vulnerability scan.

Run `uv run pytest -p no:cacheprovider`, `uv run ruff check .`, and `uv run mypy app tests` in backend,
then the frontend lint, typecheck, test, and build scripts. Regression tests cover streamed body caps,
throttle responses, untrusted forwarded headers, role permissions, and deterministic prompt-injection
defenses. Refresh rotation locks token rows and logout verifies token ownership.
