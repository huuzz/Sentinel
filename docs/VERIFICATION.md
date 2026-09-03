# Verification record

Milestone 9 verification is in progress (2026-09-03). This document distinguishes
local results from pending checks; configured CI is not proof of a passing hosted run.

## Completed locally

- Backend: Ruff, strict mypy over `app tests scripts`, and 56 pytest tests passed.
- Frontend: ESLint, TypeScript, two component tests, and production build passed.
- A pytest cache permission warning did not affect test outcomes.

## Release checklist

- [ ] Docker rebuild and health checks after the final changes.
- [ ] Seed an empty PostgreSQL database, verify 45 events and two alerts.
- [x] Seed again and verify event/evidence/alert counts do not increase.
- [ ] Capture actual dashboard and evidence screenshots using synthetic data.
- [ ] Verify locked installs and setup from a clean checkout.
- [ ] Review hosted CI and security scanner findings before deployment.

Existing-database seed verification: 45 events added; HIGH brute-force evidence count
10, MEDIUM API-volume evidence count 30. Second run added zero events and touched zero
alerts. The original 78 synthetic events were preserved.

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
