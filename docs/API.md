# API

FastAPI publishes interactive OpenAPI documentation at `/docs` and its schema at `/openapi.json`.

## Authentication and authorization

- `POST /api/v1/auth/login`, `/refresh`, and `/logout` manage rotating sessions.
- `GET /api/v1/auth/me` returns the signed-in user.
- `/api/v1/users` and `/api/v1/audit-logs` are administrator-only.
- Domain reads allow VIEWER, ANALYST, and ADMIN. Ingestion and alert status changes require ANALYST or ADMIN.

Protected calls use `Authorization: Bearer <access-token>`.

## Operational endpoints

### `GET /health/live`

Confirms the backend process can serve requests. It does not contact dependencies.

### `GET /health/ready`

Runs `SELECT 1` against PostgreSQL. Returns 200 with `status: ready`, or 503 when the database is unavailable.

Responses include `X-Request-ID`; callers may provide the header to correlate a request.

## Events

- `POST /api/v1/events` validates and stores one event, synchronously evaluates enabled rules, and returns the event plus any alert IDs.
- `GET /api/v1/events` accepts `limit`, `event_type`, `source_ip`, `user_identifier`, and `source` filters.
- `GET /api/v1/events/{event_id}` returns one event or 404.

An authentication failure is represented as `event_type: "authentication"` and `outcome: "failure"`. Timestamps must include a timezone, IP addresses are normalized, and metadata is limited to 16 KiB.

Enabled rules detect brute force, password spraying, unusual API volume, and a successful login after
repeated failures. Thresholds and windows are typed environment settings.

## Alerts and dashboard

- `GET /api/v1/alerts` accepts `limit`, `severity`, `status`, and `rule` filters.
- `GET /api/v1/alerts/{alert_id}` includes supporting security events.
- `PATCH /api/v1/alerts/{alert_id}` updates status for analysts and administrators.
- `GET /api/v1/dashboard/summary` returns totals, severity counts, common event types, hourly volume, and recent alerts.

## Advisory AI analysis

- `POST /api/v1/alerts/{alert_id}/analysis` creates or replaces an analysis for ANALYST and ADMIN.
- `GET /api/v1/alerts/{alert_id}/analysis` reads the saved analysis for every authenticated role.

The response contains a bounded summary, likely attack label, confidence from 0 to 1, evidence event
IDs, recommended human actions, and provider/model metadata. It contains no hidden reasoning.

The initial brute-force rule creates a HIGH alert after ten failures from one source IP inside two minutes. While that finding remains open, subsequent matching evidence is attached to the same alert instead of creating an alert storm.
