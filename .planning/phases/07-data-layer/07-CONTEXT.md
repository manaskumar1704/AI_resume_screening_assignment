# Phase 7: Data Layer - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Database schema migration enabling deduplication of evaluation requests.

Adds request_hash column and composite index to the evaluations table for efficient duplicate detection.

</domain>

<decisions>
## Implementation Decisions

### Migration Approach
- **D-01:** Use standard Alembic autogenerate migration to add request_hash column and composite index
- Migration should match the existing model definitions in `backend/app/models.py`

### Reversibility Strategy
- **D-02:** Include explicit downgrade function in migration
- Downgrade must remove the composite index and column without data loss
- Must be testable via `alembic downgrade` command

### Testing Approach
- **D-03:** Verify migration runs cleanly via `alembic upgrade head`
- Verify downgrade works via `alembic downgrade -1`
- Optionally verify index usage with EXPLAIN query

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Database & Migrations
- `backend/app/models.py` — Current Evaluation model with request_hash and index definitions
- `backend/alembic/versions/001_initial.py` — Existing initial migration
- `backend/alembic.ini` — Alembic configuration

### Project Documentation
- `AGENTS.md` — Database layer rules (async SQLAlchemy, migrations via Alembic)

[No external specs — requirements fully captured in decisions above]

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/models.py` already defines the target schema (request_hash column, composite index)

### Established Patterns
- Alembic migrations in `backend/alembic/versions/`
- Migration follows pattern: upgrade() adds changes, downgrade() reverses them

### Integration Points
- Migration modifies `evaluations` table
- Index enables efficient deduplication queries: WHERE request_hash = X AND status = 'pending'

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 07-data-layer*
*Context gathered: 2026-04-14*
