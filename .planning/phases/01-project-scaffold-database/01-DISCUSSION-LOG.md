# Phase 1: Project Scaffold & Database - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-13
**Phase:** 01-project-scaffold-database
**Areas discussed:** Docker setup, Python project structure, Database configuration

---

## Docker Setup

| Option | Description | Selected |
|--------|-------------|----------|
| Separate containers | postgres:17, redis:7-alpine, build context ./backend for API | ✓ |
| All-in-one container | All services in single container with compose-driven startup | |

**User's choice:** Separate containers — postgres:17, redis:7-alpine, API built from ./backend context

---

## Python Project Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Flattish | backend/app/main.py, backend/app/config.py, etc. — standard FastAPI layout | ✓ |
| Nested src/ | backend/src/app/main.py, backend/src/app/config.py, more depth | |

**User's choice:** Flattish layout — standard FastAPI structure

---

## Database Configuration

| Option | Description | Selected |
|--------|-------------|----------|
| Standard | Pool size 5, max overflow 10, recycle after 1800s | ✓ |
| High concurrency | Larger pool for high-concurrency scenarios | |

**User's choice:** Standard with modular code for future scaling

---

## Agent's Discretion

- Exact docker-compose service order (affects startup dependencies)
- Specific environment variable defaults (can be overridden in .env)
- Migration file naming convention
