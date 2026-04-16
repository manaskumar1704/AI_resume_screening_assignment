# Requirements: AI Resume Screening Service

**Defined:** 2026-04-16
**Core Value:** Reliable, async resume screening with structured LLM output and deduplication.

## v1 Requirements

### Database

- [ ] **DB-01**: .env contains Supabase DATABASE_URL with connection pooling
- [ ] **DB-02**: .env.example contains Supabase DATABASE_URL placeholder with [YOUR-PASSWORD]
- [ ] **DB-03**: API connects to Supabase PostgreSQL when DATABASE_URL points to it
- [ ] **DB-04**: Docker postgres remains available as fallback via docker-compose
- [ ] **DB-05**: Supabase connection uses session pooler mode (transaction mode not required)

### Configuration

- [ ] **CFG-01**: Supabase DATABASE_URL in .env is valid asyncpg connection string
- [ ] **CFG-02**: .env.supabase.example created with Supabase-specific template
- [ ] **CFG-03**: Documentation updated with Supabase setup instructions

### Migrations

- [ ] **MIG-01**: alembic upgrade head runs successfully on Supabase
- [ ] **MIG-02**: Existing schema created without modification
- [ ] **MIG-03**: All PostgreSQL-specific types work on Supabase

### Testing

- [ ] **TST-01**: /health/ready returns 200 when connected to Supabase
- [ ] **TST-02**: Full evaluation flow works with Supabase database
- [ ] **TST-03**: Duplicate detection works with Supabase

## v2 Requirements

(Not in current scope)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Local SQLite | Supabase provides hosted dev database |
| Multiple database backends | Single Supabase primary sufficient |
| Automatic failover | Manual DATABASE_URL switch |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DB-01 | Phase 1 | Complete |
| DB-02 | Phase 1 | Complete |
| DB-03 | Phase 1 | Complete |
| DB-04 | Phase 2 | Complete |
| DB-05 | Phase 1 | Complete |
| CFG-01 | Phase 1 | Complete |
| CFG-02 | Phase 1 | Complete |
| CFG-03 | Phase 2 | Complete |
| MIG-01 | Phase 1 | Complete |
| MIG-02 | Phase 1 | Complete |
| MIG-03 | Phase 1 | Complete |
| TST-01 | Phase 2 | Complete |
| TST-02 | Phase 2 | Complete |
| TST-03 | Phase 2 | Complete |

**Coverage:**
- v1 requirements: 14 total
- Mapped to phases: 0 (pending roadmap)
- Unmapped: 14 ⚠️

---
*Requirements defined: 2026-04-16*
*Last updated: 2026-04-16 after milestone v1.1 started*