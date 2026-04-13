# Roadmap: AI Resume Screening Service

## Project Overview

An async backend service that screens PDF resumes against Job Descriptions using an LLM.

---

## Current Milestone

**v1.1** - (In Progress)

---

## Previous Milestone

### v1.0: Core Backend - COMPLETE ✅

| Phase | Status |
|-------|--------|
| 1: Project Scaffold & Database | Complete |
| 2: Evaluate Endpoints | Complete |
| 3: LLM Service | Complete |
| 4: ARQ Worker with Retry | Complete |
| 5: Integration Tests | Complete |

**v1.0 Summary:** Full backend implementation with FastAPI, ARQ worker, PostgreSQL, and LLM integration. All 5 integration tests pass.

---

## Future Work

The following features are planned for future milestones:

### Frontend Development
- Next.js 15 application
- shadcn/ui components
- Upload UI for PDF resumes
- Results dashboard

### Infrastructure
- Docker optimization
- Health check endpoints
- Metrics and monitoring

### Enhancements
- Authentication/Authorization
- Rate limiting at API level
- Batch processing
- Webhook notifications

---

## Canonical References

- **AGENTS.md** — Source of truth for all implementation rules
- **DESIGN.md** — Frontend design system ("Dossier Framework")
- **backend/prompts/resume_screening.md** — LLM system prompt (must be external)
- **.planning/milestones/v1.0/MILESTONE.md** — v1.0 complete summary