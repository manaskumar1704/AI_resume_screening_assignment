# Roadmap: Milestone v1.1 Connect to Supabase

**Created:** 2026-04-16
**2 phases** | **14 requirements** | All covered ✓ ✓ COMPLETE

---

## Phase 1: Configure Supabase Connection

**Goal:** Connect API to Supabase PostgreSQL and verify migrations work.

**Requirements:** DB-01, DB-02, DB-03, DB-05, CFG-01, CFG-02, MIG-01, MIG-02, MIG-03

**Success Criteria:**

1. `.env` contains valid Supabase DATABASE_URL with [YOUR-PASSWORD] replaced
2. `.env.example` contains Supabase placeholder with [YOUR-PASSWORD]
3. API starts and connects to Supabase when DATABASE_URL is Supabase URL
4. `alembic upgrade head` runs successfully on Supabase
5. All existing schema tables created correctly on Supabase
6. /health/ready returns 200 with Supabase connection

---

## Phase 2: Fallback & Verification

**Goal:** Keep Docker PostgreSQL as fallback and verify full evaluation flow.

**Requirements:** DB-04, CFG-03, TST-01, TST-02, TST-03

**Success Criteria:**

1. docker-compose still runs local postgres (unchanged)
2. README updated with Supabase setup instructions
3. /health/ready returns 200 when connected to Supabase
4. Full POST /api/v1/evaluate → GET /api/v1/evaluate/{id} works with Supabase
5. Duplicate request detection works with Supabase

---

## Phase Details

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | Configure Supabase Connection | Connect API to Supabase PostgreSQL and verify migrations work | DB-01, DB-02, DB-03, DB-05, CFG-01, CFG-02, MIG-01, MIG-02, MIG-03 | 6 |
| 2 | Fallback & Verification | Keep Docker PostgreSQL as fallback and verify full evaluation flow | DB-04, CFG-03, TST-01, TST-02, TST-03 | 5 |

---

*Roadmap created: 2026-04-16*
*Last updated: 2026-04-16 after milestone v1.1 started*