# Threat Model

## Assets and trust boundaries

Assets include user identities, refresh tokens, security telemetry, alerts, AI analyses, database integrity, and provider credentials. Trust boundaries exist at the browser/API edge, simulator ingestion, database connection, and future AI/embedding providers.

| Threat | Impact | Planned mitigation |
|---|---|---|
| Malformed or oversized telemetry | Resource exhaustion or corrupt analysis | Strict schemas, size/range limits, bounded queries, rate limits |
| Broken authorization | Exposure or unauthorized alert changes | Backend RBAC, deny-by-default dependencies, role matrix tests |
| Credential/token theft | Account takeover | Argon2id, short access lifetime, hashed rotating refresh tokens, secure cookies |
| SQL injection | Database compromise | ORM parameterization, validation, least-privileged credentials |
| Alert flooding | Analyst fatigue and storage growth | Rule deduplication, ingestion limits, bounded evidence |
| Prompt injection in logs or retrieved text | Misleading AI output or data disclosure | Instruction/data separation, minimal context, schema validation, no tools or actions |
| Secret leakage through logs/prompts | Credential exposure | Redaction, allowlisted context, no full prompt or token logging |
| Unsafe simulator targeting | Harm to external systems | Synthetic events only; local/explicit SentinelAI endpoint allowlist |
| Supply-chain compromise | Malicious dependency or image | Lockfiles, review, dependency/secret scanning, pinned CI actions |

The AI is an explanation assistant, not a detector or remediation agent. A human remains in control.

Milestone 3 implements this boundary with allowlisted event fields, bounded context/output, evidence
reference validation, a provider-neutral interface, and a deterministic offline provider for tests and
local demonstrations.
