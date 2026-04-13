# Phase 7: Data Layer - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-14
**Phase:** 7-Data Layer
**Areas discussed:** Migration approach, Reversibility strategy, Testing approach

---

## Migration Approach

| Option | Description | Selected |
|--------|-------------|----------|
| Standard Alembic autogenerate migration | Use `alembic revision --autogenerate` to create migration matching model | ✓ |
| Manual migration | Write migration manually without autogenerate | |
| Custom script | Use raw SQL script outside Alembic | |

**User's choice:** Standard Alembic autogenerate migration
**Notes:** Migration should match existing model definitions in `backend/app/models.py`

---

## Reversibility Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Include explicit downgrade | Add downgrade function that removes column/index | ✓ |
| Make migration non-reversible | Mark with `non_deterministic` if needed | |
| No downgrade needed | Accept data loss on downgrade | |

**User's choice:** Include explicit downgrade in migration
**Notes:** Downgrade must remove the composite index and column without data loss

---

## Testing Approach

| Option | Description | Selected |
|--------|-------------|----------|
| Verify upgrade and downgrade | Run both `alembic upgrade head` and `alembic downgrade -1` | ✓ |
| Only verify upgrade | Just test that migration applies | |
| Manual EXPLAIN check | Query explain plans to verify index usage | |

**User's choice:** Verify migration runs cleanly via alembic upgrade, verify downgrade works via alembic downgrade
**Notes:** Optionally verify index usage with EXPLAIN query

---

## Deferred Ideas

None — discussion stayed within phase scope.
