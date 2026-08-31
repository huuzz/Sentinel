# API

FastAPI publishes interactive OpenAPI documentation at `/docs` and its schema at `/openapi.json`.

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

## Alerts and dashboard

- `GET /api/v1/alerts` accepts `limit`, `severity`, `status`, and `rule` filters.
- `GET /api/v1/alerts/{alert_id}` includes supporting security events.
- `GET /api/v1/dashboard/summary` returns totals, severity counts, common event types, hourly volume, and recent alerts.

The initial brute-force rule creates a HIGH alert after ten failures from one source IP inside two minutes. Findings are deduplicated by rule, source, and time bucket.
