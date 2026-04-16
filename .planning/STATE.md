## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-04-16 — Milestone v1.1 started

---

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-16)

**Core value:** Reliable, async resume screening with structured LLM output and deduplication.
**Current focus:** Connecting to Supabase PostgreSQL

---

## Accumulated Context

### Technology Stack

- FastAPI + ARQ worker for async processing
- PostgreSQL 17 with async SQLAlchemy 2.0
- LangChain for LLM orchestration
- Supabase hosted PostgreSQL (this milestone)

### Current Configuration

- DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/resume_screener (to be updated)
- LLM_PROVIDER: groq
- Redis via docker-compose

### Known Workarounds

- None currently