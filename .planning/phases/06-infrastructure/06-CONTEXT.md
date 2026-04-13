# Phase 6: Infrastructure - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Production-ready backend with config validation, structured logging, health checks, and metrics. This phase adds observability infrastructure—logging, health endpoints, and monitoring—without changing the evaluation pipeline.

</domain>

<decisions>
## Implementation Decisions

### Structured Logging
- **D-01:** Use structlog 25.x with JSON output in production, pretty console in dev
- **D-02:** All API requests include correlation IDs in log context

### Health Checks
- **D-03:** Separate endpoints: /health/live (liveness) and /health/ready (readiness)
- **D-04:** /health/ready verifies both database AND Redis connectivity

### Metrics
- **D-05:** Use prometheus-fastapi-instrumentator for automatic HTTP metrics
- **D-06:** Exclude /health and /metrics endpoints from metrics collection

### Config Validation
- **D-07:** Use pydantic-settings for validation at startup
- **D-08:** Fail fast with clear error message if required config is missing

### the agent's Discretion
- Exact log field names and structure
- Metrics label names and cardinalities
- Error response formats for health endpoints

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Config
- `backend/app/config.py` — Current pydantic-settings configuration
- `AGENTS.md` — Config via environment variables requirement

### Logging
- `AGENTS.md` — No print() logging requirement
- `.planning/research/STACK.md` — structlog 25.x selection

### Health
- `.planning/research/FEATURES.md` — Health check requirements
- `.planning/research/PITFALLS.md` — Health check pitfalls

### Metrics
- `.planning/research/FEATURES.md` — Prometheus requirements

[If no external specs: "No external specs — requirements fully captured in decisions above"]

</canonical_refs>

<specifics>
## Specific Ideas

- "JSON output in production for log aggregation"
- "Standard Kubernetes probe patterns"

</specifics>

<deferred>
## Deferred Ideas

- None — all discussed within phase scope

</deferred>

---

*Phase: 06-infrastructure*
*Context gathered: 2026-04-14*