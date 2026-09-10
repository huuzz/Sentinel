# Portfolio demo

This is synthetic security telemetry, not a real attack. No traffic is sent to the
example source addresses. Use a local development database with default detection settings.

## Prepare

Follow the root README to start Docker and bootstrap an administrator. Sign in at
http://localhost:3000. From the repository root, run:

```sh
docker compose exec backend python -m scripts.seed_demo --confirm-synthetic
```

If the stack uses a named Compose project, add `-p YOUR_PROJECT` after `compose`.
The CLI uses the backend ingestion service directly, not HTTP; this demonstrates
detection and persistence but is not an authentication or rate-limit test.
It requires `SENTINEL_ENVIRONMENT=development` and does not create accounts.

The dataset contains five successful logins, ten failed logins from one reserved
address, and thirty example API requests. On an empty database with default settings,
expect 45 events, one HIGH brute-force alert and one MEDIUM API-volume alert.
Existing telemetry can affect aggregate totals and evidence; use an isolated database
for exact counts. The source label is `sentinel-portfolio-v1`.

Run the command once at a time. Sequential reruns skip existing seed indexes and
resume partially completed runs. They do not delete data or reset timestamps; an old
seed will not produce new "today" totals. Do not delete a real database to reset a demo.

## Three-minute recording

1. Overview (30 seconds): explain deterministic rules and aggregate counts. Refresh
   the page after seeding. Show that these are simulated events.
2. Events (30 seconds): show successful versus failed authentication and structured
   fields, rather than interpreting arbitrary log prose.
3. Alert evidence (45 seconds): open the HIGH brute-force finding and show the ten
   linked failures, rule identity, severity, and risk score.
4. Advisory analysis (30 seconds): generate the local explanation. Identify it as
   a deterministic fake provider, not an external LLM or autonomous responder.
5. Limitations (45 seconds): explain synthetic ML training, development-only deployment,
   backend role enforcement, and the distinction between implemented controls and
   independently verified security.

## Screenshot checklist

Capture the actual running overview, HIGH alert with evidence, and advisory analysis.
Use only synthetic data; exclude passwords, browser storage, cookies, tokens, terminal
credentials, and unrelated tabs. Label captures with the commit and dataset source.
Store reviewed images under `docs/images/`; do not substitute mockups for working UI.

## Screenshots

The screenshots from the previous name were removed during the Sentinel rename.
Capture replacements after the local Docker stack is available. Use the checklist
above and record the commit and dataset source with each image.
