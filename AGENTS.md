# SentinelAI agent guide

SentinelAI is an educational, portfolio-quality security monitoring platform. It is a Next.js frontend plus a modular FastAPI backend using PostgreSQL.

## Working rules

- Inspect existing code and documentation before changing it. Keep changes focused and understandable.
- Preserve the API unless an intentional change is documented.
- Backend code belongs in routes, schemas, services, repositories, detection, or infrastructure according to responsibility; do not put business logic in routes.
- Treat events and AI/RAG context as untrusted. Validate and bound input. Never log secrets, credentials, tokens, or full prompts.
- The simulator may create synthetic telemetry only and may target only configured SentinelAI development endpoints. Never add scanning, exploitation, credential attacks, malware, persistence, or destructive behavior.
- Do not add major dependencies or infrastructure without a concrete requirement and documented rationale. Never commit secrets.
- Update relevant docs when behavior or architecture changes.
- Run relevant tests, lint, type checks, and builds. Report failures honestly.

## Commands

- Stack: `docker compose up --build`
- Backend: `cd backend && uv sync && uv run pytest && uv run ruff check . && uv run mypy app tests`
- Frontend: `cd frontend && npm ci && npm run lint && npm run typecheck && npm test && npm run build`
