# Phase 1: Project Scaffold & Database - Task Specs

**Phase:** 01-project-scaffold-database
**Generated:** 2026-04-13

---

## Phase Overview

**Goal:** Set up the project structure, Docker environment, and PostgreSQL schema with Alembic.

**Observable Truths:**
- Docker containers start successfully
- Database migrations run without error
- Async engine connects to PostgreSQL
- .env.example documents all required environment variables

---

## Decision Coverage Matrix

| Decision ID | Description | Plan | Task |
|------------|-------------|------|------|
| D-01 | Separate containers (postgres:17, redis:7-alpine, API) | 01 | 1 |
| D-02 | Service names: postgres, redis, api | 01 | 1 |
| D-03 | Healthchecks on all services | 01 | 1 |
| D-04 | Volume mounts for persistent data | 01 | 1 |
| D-05 | Flattish layout (backend/app/) | 01 | 2 |
| D-06 | Standard FastAPI structure | 01 | 2 |
| D-07 | pyproject.toml at backend/ root | 01 | 2 |
| D-08 | Pool settings: pool_size=5, max_overflow=10, pool_recycle=1800 | 02 | 1 |
| D-09 | Modular code for pool settings | 02 | 1 |
| D-10 | Async SQLAlchemy 2.0 + asyncpg | 02 | 1 |
| D-11 | Alembic migrations in backend/alembic/versions/ | 03 | 1 |

---

## Task Specifications

### Task 1: Docker Compose + Python Dependencies + Environment Template

**Files:** docker-compose.yml, backend/pyproject.toml, .env.example

**Action:** Create foundational infrastructure files.

**docker-compose.yml:**
- postgres:17 service with healthcheck (pg_isready)
- redis:7-alpine service with healthcheck
- api service built from ./backend context
- Volume mounts: postgres data, redis data
- Service names: postgres, redis, api (per D-02)
- Healthchecks on all services (per D-03)
- Peristent volumes (per D-04)

**backend/pyproject.toml:**
- Python 3.13
- Dependencies: fastapi[standard], sqlalchemy[asyncio]=2.0.*, asyncpg, alembic, pydantic-settings, langchain-core, langchain, arq, pdfplumber, tenacity, python-multipart
- uv for dependency management

**.env.example:**
- LLM settings: LLM_PROVIDER, LLM_MODEL, OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY
- Database: DATABASE_URL
- Redis: REDIS_URL
- App: DEBUG

**Verify:** `docker-compose config` validates successfully

**Done:** All three files created with correct structure per locked decisions

---

### Task 2: Database Layer + Models

**Files:** backend/app/database.py, backend/app/models.py

**Action:** Create async SQLAlchemy engine and Evaluation model.

**backend/app/database.py:**
- Async engine with create_async_engine()
- pool_size=5, max_overflow=10, pool_recycle=1800 (per D-08)
- Async session factory with async_sessionmaker
- Modular pool settings via config (per D-09)
- Async SQLAlchemy 2.0 with asyncpg driver (per D-10)

**backend/app/models.py:**
- Base: declarative_base()
- Evaluation table with columns:
  - id (UUID, primary key)
  - status (VARCHAR(20), default 'pending')
  - resume_filename (TEXT)
  - jd_text (TEXT)
  - score (INTEGER, nullable)
  - verdict (VARCHAR(50), nullable)
  - missing_requirements (JSONB, nullable)
  - justification (TEXT, nullable)
  - confidence (FLOAT, nullable)
  - match_percentages (JSONB, nullable)
  - extracted_skills (JSONB, nullable)
  - error_message (TEXT, nullable)
  - created_at (TIMESTAMPTZ, default NOW())
  - updated_at (TIMESTAMPTZ, default NOW())

**Verify:** `python -c "from app.models import Evaluation; print('models OK')"`

**Done:** Engine connects to PostgreSQL (tested via docker-compose), Evaluation table defined

---

### Task 3: Alembic Configuration + Initial Migration

**Files:** backend/alembic.ini, backend/alembic/versions/001_initial.py

**Action:** Configure Alembic and create initial migration.

**backend/alembic.ini:**
- sqlalchemy.url from DATABASE_URL env var
- Migration locations: backend/alembic/versions/
- Standard template configuration

**backend/alembic/env.py:**
- Import models.Base and models
- Configure async engine connection

**backend/alembic/versions/001_initial.py:**
- Creates evaluations table matching models.py schema
- Primary key, indexes, constraints

**Verify:** `docker-compose exec api alembic current` shows no revisions, or `alembic upgrade head` runs successfully

**Done:** Initial migration creates Evaluation table in PostgreSQL

---

## Wave Structure

| Wave | Tasks | Autonomous |
|------|-------|------------|
| 1 | Task 1 (docker-compose, pyproject, .env.example) | yes |
| 2 | Task 2 (database.py, models.py) | yes |
| 3 | Task 3 (alembic.ini, migration) | yes |

---

## Dependencies

```
Task 1 (docker-compose.yml, pyproject.toml, .env.example)
  └── needs: nothing (foundational)
  └── creates: Docker + Python project structure

Task 2 (database.py, models.py)
  └── needs: pyproject.toml (for dependencies)
  └── creates: Async engine + Evaluation model

Task 3 (alembic.ini, initial migration)
  └── needs: models.py (for table definition)
  └── creates: Alembic config + migration file
```

---

## Next Steps

After task specs approval: `/gsd-execute-phase 01-project-scaffold-database`

Execute in wave order: Wave 1 → Wave 2 → Wave 3