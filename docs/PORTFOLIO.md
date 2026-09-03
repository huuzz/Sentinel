# Explaining SentinelAI

## Short introduction

SentinelAI is an educational security-monitoring application built with Next.js,
FastAPI, and PostgreSQL. Structured synthetic events produce deterministic findings
with linked evidence. AI explanations and ML anomaly scores are advisory; neither
performs remediation or establishes that an attack occurred.

## Design tradeoffs to discuss

- A modular monolith keeps transactions and operations understandable. Services and
  repositories separate application logic from HTTP and persistence.
- Synchronous detection makes ingestion-to-alert demonstrations deterministic. Higher
  throughput would require measured query improvements or durable background jobs.
- PostgreSQL stores relational records, bounded JSON telemetry, and knowledge vectors.
  One database reduces infrastructure, but requires index and retention planning.
- Access tokens stay in memory; rotating refresh tokens use HttpOnly cookies and
  server-side hashes. Backend role checks remain authoritative over UI controls.
- Deterministic local providers make tests reproducible without paid requests. They
  demonstrate interfaces and validation, not the quality of a production language model.

## Honest resume examples

- Built a Next.js/FastAPI security-monitoring portfolio application with PostgreSQL,
  transactional event ingestion, four deterministic detection rules, and linked evidence.
- Implemented role-based authorization, Argon2 password hashing, rotating refresh
  sessions, and audit records, with automated backend regression tests.
- Added advisory synthetic-data anomaly scoring and cited knowledge retrieval behind
  provider interfaces, plus Docker-based local development and CI workflows.

Use only claims you can explain and demonstrate. Do not claim production deployment,
real attack prevention, enterprise scale, or measured detection accuracy.

## Known limitations

- Educational local application, not a production SOC service or penetration-testing tool.
- Current AI provider is deterministic; local embedding similarity is not equivalent
  to a trained semantic embedding model.
- Isolation Forest training uses synthetic data. Scores are not attack probabilities.
- Cursor-shaped list responses do not yet implement complete cursor navigation.
- Process-local rate limits reset on restart and do not coordinate multiple replicas;
  proxy routing can cause clients to share an IP quota.
- Demo seeding is an operator-only development utility. Run one invocation at a time.
- Cloud configuration, backups, TLS termination, and operational recovery remain
  deployment work requiring approval. Hosted scanner results still need review.
- Automated UI coverage is narrower than backend coverage; recorded screenshots are
  point-in-time evidence, not a substitute for accessibility and end-to-end tests.

See [demo instructions](DEMO.md), [threat model](THREAT_MODEL.md), and
[cloud design](CLOUD_DEPLOYMENT_DESIGN.md) for the corresponding scope and safeguards.
