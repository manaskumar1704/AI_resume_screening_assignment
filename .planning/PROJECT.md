# AI Resume Screening Service

## What This Is

An async backend service that screens PDF resumes against job descriptions using an LLM. Resumes are uploaded via REST API, processed in the background by an ARQ worker, and scored against required skills with structured JSON output persisted to PostgreSQL.

## Core Value

Reliable, async resume screening with structured LLM output and deduplication.

---

## Current Milestone: v1.1 Connect to Supabase

**Goal:** Switch from Docker PostgreSQL to hosted Supabase PostgreSQL for production parity and remove local DB dependency.

**Target features:**
- Connect to Supabase hosted PostgreSQL
- Keep Docker PostgreSQL as fallback/development
- Preserve same schema and migrations (production parity)
- Update all environment configurations

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

## Requirements

### Validated

(Validated from previous development - see git history)

### Active

- [ ] Connect to Supabase hosted PostgreSQL
- [ ] Update .env with Supabase DATABASE_URL
- [ ] Update .env.example with Supabase placeholder
- [ ] Keep docker-compose postgres as fallback
- [ ] Verify migrations work on Supabase
- [ ] Test full evaluation flow with Supabase

### Out of Scope

- Local SQLite for development (Supabase serves this purpose)
- Multiple database backends (single Supabase primary)

## Context

**Current state:**
- Docker PostgreSQL 17 running locally via docker-compose
- Async SQLAlchemy 2.0 with asyncpg driver
- Existing schema with evaluations table, request_hash, status tracking
- Migrations using Alembic

**Supabase Configuration:**
- Host: db.zaasopywtnokbrwueupa.supabase.co
- Port: 5432
- Pooler: Session Pooler mode

## Constraints

- **Database:** Must use asyncpg driver (Supabase connection pooler)
- **Schema:** Same as current - PostgreSQL-specific types must work
- **Migrations:** Alembic must run on Supabase without modification

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Supabase over local Docker | Production parity, no local DB dependency | ✓ Connected (IPv4) |
| Keep Docker postgres as fallback | Development flexibility, offline work | ✓ Available |
| Environment-based config | Easy switch between Supabase/local | ✓ Works |
| Supabase free tier | IPv4 now works via pooler | ✓ Works |

---

*Last updated: 2026-04-16 after milestone v1.1 started*