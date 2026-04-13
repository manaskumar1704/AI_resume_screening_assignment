# Roadmap: AI Resume Screening Service

## Project Overview

An async backend service that screens PDF resumes against Job Descriptions using an LLM.

---

## Milestones

- ✅ **v1.0 Core Backend** — Phases 1-5 (shipped 2026-04-13)
- 🚧 **v1.1 Production & Frontend** — Phases 6-7 (in progress)

---

## Phases

- [x] **Phase 6: Infrastructure** — Config validation, structured logging, health checks, metrics (completed 2026-04-13)
- [ ] **Phase 7: Data Layer** — Alembic migration for request_hash, indexes

---

## Phase Details

### Phase 6: Infrastructure
**Goal**: Production-ready backend with config validation, structured logging, health checks, and metrics

**Depends on**: Phase 5 (v1.0 completion)

**Requirements**: INFR-01, INFR-02, INFR-03, INFR-04, INFR-05

**Success Criteria** (what must be TRUE):
1. API fails fast at startup if required config is missing (observable: app exits with clear error message)
2. Every API request logs with correlation ID in structured JSON format (observable: logs contain request_id)
3. GET /health/live returns 200 when process is running (observable: curl localhost:8000/health/live returns 200)
4. GET /health/ready returns 200 when both DB and Redis are reachable (observable: curl localhost:8000/health/ready returns 200)
5. GET /metrics returns Prometheus-formatted metrics (observable: curl localhost:8000/metrics returns text/plain with evaluation counts)

**Plans**: 2 plans (06-01-PLAN.md, 06-02-PLAN.md)

### Phase 7: Data Layer
**Goal**: Database schema migration enabling deduplication of evaluation requests

**Depends on**: Phase 6

**Requirements**: DATA-01, DATA-02, DATA-03

**Success Criteria** (what must be TRUE):
1. Evaluations table has request_hash column (observable: SELECT request_hash FROM evaluations LIMIT 1 works)
2. Composite index exists on (request_hash, status) for deduplication queries (observable: EXPLAIN shows index usage)
3. Migration can be reverted without data loss (observable: alembic downgrade executes successfully)

**Plans**: TBD
**UI hint**: no

---

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 6. Infrastructure | 2/2 | Complete    | 2026-04-13 |
| 7. Data Layer | 0/1 | Not started | - |

---

## Future Work

### Deferred to v2

The following features are planned for future milestones:

**Frontend Development**
- Next.js 15 application with upload page and results dashboard
- shadcn/ui components
- Docker Compose integration

**Enhancements**
- Rate limiting at API level
- Batch processing
- Webhook notifications

---

## Canonical References

- **AGENTS.md** — Source of truth for all implementation rules
- **DESIGN.md** — Frontend design system ("Dossier Framework")
- **backend/prompts/resume_screening.md** — LLM system prompt (must be external)