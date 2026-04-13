# Phase 1: Project Scaffold & Database - Context

**Gathered:** 2026-04-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Set up the project structure, Docker environment, and PostgreSQL schema with Alembic. This creates the foundation for all subsequent phases — no business logic here, just infrastructure and configuration.

</domain>

<decisions>
## Implementation Decisions

### Docker Setup
- **D-01:** Separate containers — postgres:17, redis:7-alpine, API built from ./backend context
- **D-02:** Service names: postgres, redis, api (for consistency with AGENTS.md)
- **D-03:** Healthchecks on all services
- **D-04:** Volume mounts for persistent data (postgres data, redis data)

### Python Project Structure
- **D-05:** Flattish layout — backend/app/main.py, backend/app/config.py, not nested src/
- **D-06:** Standard FastAPI structure: main.py (app factory), config.py, database.py, models.py, schemas.py, api/, services/, worker/
- **D-07:** pyproject.toml at backend/ root with all dependencies

### Database Configuration
- **D-08:** Standard pool settings: pool_size=5, max_overflow=10, pool_recycle=1800
- **D-09:** Code must be modular to scale pool settings via config
- **D-10:** Async SQLAlchemy 2.0 with asyncpg driver
- **D-11:** Alembic for migrations, migrations stored in backend/alembic/versions/

### Agent's Discretion
- Exact docker-compose service order (affects startup dependencies)
- Specific environment variable defaults (can be overridden in .env)
- Migration file naming convention

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Infrastructure
- `AGENTS.md` — Source of truth for all implementation rules, tech stack versions

### Database
- `backend/app/models.py` — Will define the Evaluation table schema (Phase 1 task)

[No external specs — requirements fully captured in decisions above]

</canonical_refs>

## Existing Code Insights

### Reusable Assets
- None yet — this is the foundation phase

### Established Patterns
- Async SQLAlchemy 2.0 + asyncpg for PostgreSQL (from AGENTS.md)
- FastAPI app factory pattern (from AGENTS.md)
- Alembic for migrations (from AGENTS.md)

### Integration Points
- Docker Compose orchestrates all services
- Backend Dockerfile builds Python dependencies from pyproject.toml
- Database connection string passed via DATABASE_URL env var

</code_context>

<specifics>
## Specific Ideas

- Code should be modular enough to scale pool settings when needed
- Service names match AGENTS.md conventions: postgres, redis, api

</specifics>

<deferred>
## Deferred Ideas

None — Phase 1 scope is clear

</deferred>

---

*Phase: 01-project-scaffold-database*
*Context gathered: 2026-04-13*