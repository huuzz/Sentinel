# Verification record

Milestone 9 local verification completed on 2026-09-03. This document distinguishes
local results from pending checks; configured CI is not proof of a passing hosted run.

## Completed locally

- Backend: Ruff, strict mypy over `app tests scripts`, and 56 pytest tests passed.
- Frontend: ESLint, TypeScript, two component tests, and production build passed.
- A pytest cache permission warning did not affect test outcomes.

## Release checklist

- [x] Docker rebuild and health checks after the final changes.
- [x] Seed an empty PostgreSQL database, verify 45 events and two alerts.
- [x] Seed again and verify event/evidence/alert counts do not increase.
- [x] Capture actual dashboard and evidence screenshots using synthetic data.
- [x] Verify locked installs and quality checks from a clean checkout.
- [ ] Review hosted CI and security scanner findings before deployment.

Existing-database seed verification: 45 events added; HIGH brute-force evidence count
10, MEDIUM API-volume evidence count 30. Second run added zero events and touched zero
alerts. The original 78 synthetic events were preserved.

Isolated PostgreSQL database `sentinel_m9_verify`: migrations reached `20260903_06`;
seed created exactly 45 events, two alerts (HIGH and MEDIUM), and 40 evidence links.
A second invocation added zero events and touched zero alerts.

A clean local clone of commit `13a8843` passed `uv sync --locked`, Ruff, strict mypy,
and all 56 backend tests with no cache warning. Its frontend passed `npm ci`, ESLint,
TypeScript, both component tests, and the production build. npm reported no known
dependency vulnerabilities at install time, but emitted ESLint and whatwg-encoding
deprecation notices; these are maintenance follow-ups, not a security certification.
Docker Compose also built both images from that clean checkout and started all three
services. PostgreSQL and backend health checks passed; `/health/ready` returned `ready`
and the frontend returned HTTP 200. The temporary database was removed after
verification; the main development database was preserved. Local browser checks covered
the populated overview, seeded alert evidence, and generating a fake advisory analysis.

Scope: clean checkout was cloned locally from the committed repository, not downloaded
using a new GitHub account. Locked installs, quality checks, Docker build/start, migrations,
and seeding were exercised. Manual external PostgreSQL provisioning and cloud deployment
were not tested. Later commits add screenshots and this verification record only.

## Reproduce from a clean checkout

Run each command from the indicated directory, checking its exit code before proceeding.

```sh
git clone https://github.com/huuzz/SentinalAI.git
cd SentinalAI
cp .env.example .env
# Set your local database password and JWT secret in .env; never commit this file.
docker compose up --build -d
docker compose ps
docker compose exec backend python -m scripts.bootstrap_admin --email admin@example.com
docker compose exec backend python -m scripts.seed_demo --confirm-synthetic
docker compose exec backend python -m scripts.seed_demo --confirm-synthetic
```

On PowerShell use `Copy-Item .env.example .env`. The second seed invocation should
report zero additions. Open http://localhost:3000 and sign in with the administrator
you created. Inspect events, the HIGH alert, and its evidence. Check backend readiness
at http://localhost:8000/health/ready. Existing projects using these ports must be
stopped or given different port mappings; never reset their volumes as a workaround.

For quality checks, install the locked development dependencies:

```sh
cd backend
uv sync --locked
uv run ruff check .
uv run mypy app tests scripts
uv run pytest
cd ../frontend
npm ci
npm run lint
npm run typecheck
npm test
npm run build
```

Database-independent tests do not replace PostgreSQL migration, transaction, and
deduplication checks. No paid API credentials are needed. Keep real user data out of
test databases. `docker compose down` preserves data; do not add `-v` casually.
