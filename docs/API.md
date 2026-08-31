# API

FastAPI publishes interactive OpenAPI documentation at `/docs` and its schema at `/openapi.json`.

## Operational endpoints

### `GET /health/live`

Confirms the backend process can serve requests. It does not contact dependencies.

### `GET /health/ready`

Runs `SELECT 1` against PostgreSQL. Returns 200 with `status: ready`, or 503 when the database is unavailable.

Responses include `X-Request-ID`; callers may provide the header to correlate a request. Domain endpoints will be introduced under `/api/v1` in Milestone 1.
