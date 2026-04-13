# Roadmap: AI Resume Screening Service

## Project Overview

An async backend service that screens PDF resumes against Job Descriptions using an LLM.

---

## Milestones

- ✅ **v1.0 Core Backend** — Phases 1-5 (shipped 2026-04-13)
- 🚧 **v1.1 Production & Frontend** — Phases 6+ (in progress)

---

## Current Milestone

**v1.1** - (In Progress)

<details>
<summary>✅ v1.0 Core Backend (Phases 1-5) — SHIPPED 2026-04-13</summary>

- [x] Phase 1: Project Scaffold & Database (3/3 plans) — completed 2026-04-13
- [x] Phase 2: Evaluate Endpoints (1/1 plan) — completed 2026-04-13
- [x] Phase 3: LLM Service (1/1 plan) — completed 2026-04-13
- [x] Phase 4: ARQ Worker with Retry (1/1 plan) — completed 2026-04-13
- [x] Phase 5: Integration Tests (1/1 plan) — completed 2026-04-13

</details>

### v1.1 Production & Frontend (In Progress / Planned)

- [ ] Phase 6: Production Embellishments
- [ ] Phase 7: Frontend Development

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