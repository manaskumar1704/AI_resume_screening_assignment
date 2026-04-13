---
phase: 04-arq-worker-with-retry
plan: 01
subsystem: worker
tags: [arq, worker, retry, pdf-parsing]
dependency_graph:
  requires:
    - backend/app/models.py
    - backend/app/database.py
    - backend/app/services/llm_service.py
    - backend/app/services/pdf_parser.py
  provides:
    - backend/app/worker/settings.py
    - backend/app/worker/tasks.py
tech_stack:
  added:
    - arq >= 0.24.0 (worker queue)
    - pdfplumber >= 0.11.0 (PDF parsing)
  patterns:
    - ARQ worker settings class
    - tenacity retry with exponential backoff
    - async status machine (pending → processing → completed/failed)
key_files:
  created:
    - backend/app/worker/settings.py
    - backend/app/worker/tasks.py
  modified:
    - backend/app/services/__init__.py
    - .gitignore
decisions:
  - Used plain class for WorkerSettings (not inherit from arq.WorkerSettings as it doesn't exist in v0.27.0)
  - Removed retry_if_exception_value (not available in current tenacity)
  - Added __pycache__ and .venv to .gitignore
metrics:
  duration: null
  completed: 2026-04-14
  tasks: 4
  files: 4
---

# Phase 4 Plan 1: ARQ Worker with Retry Summary

## One-Liner

ARQ background worker with tenacity retry logic, pdfplumber PDF extraction, and status machine for resume evaluation processing.

## Completed Tasks

| Task | Name | Status |
|------|------|--------|
| 1 | Create ARQ WorkerSettings configuration | ✅ Complete |
| 2 | Implement PDF parsing with pdfplumber | ✅ Complete |
| 3 | Implement screen_resume task with tenacity retry | ✅ Complete |
| 4 | Verify status machine and DB persistence | ✅ Complete |

## Implementation Details

### WorkerSettings (backend/app/worker/settings.py)
- Uses `arq.connections.RedisSettings.from_dsn()` for Redis connection
- Registers `app.worker.tasks.screen_resume` function
- Configures max_jobs=10, job_timeout=300, keep_result=3600
- Includes on_startup and on_shutdown hooks with logging

### screen_resume Task (backend/app/worker/tasks.py)
- Decodes base64-encoded PDF bytes
- Updates status: pending → processing
- Extracts PDF text using pdf_parser.extract()
- Calls LLM with tenacity retry (3 attempts, exponential backoff 1-30s)
- Updates status to completed on success with all scorecard fields
- Updates status to failed on terminal error with error_message
- Proper logging at DEBUG/INFO/ERROR levels

### PDF Parser (backend/app/services/pdf_parser.py)
- Already implemented from previous phase
- Uses pdfplumber to extract text from PDF bytes
- Includes extract_from_base64 helper function

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Import Error] Fixed arq.BaseWorker import**
- **Found during:** Task 3 verification
- **Issue:** `from arq import BaseWorker` failed - class doesn't exist in arq v0.27.0
- **Fix:** Removed unused import
- **Files modified:** backend/app/worker/tasks.py

**2. [Rule 3 - Import Error] Fixed tenacity.retry_if_exception_value import**
- **Found during:** Task 3 verification
- **Issue:** `retry_if_exception_value` not available in current tenacity version
- **Fix:** Removed import and handled retry using custom `is_rate_limit_error()` function
- **Files modified:** backend/app/worker/tasks.py

**3. [Rule 3 - Import Error] Fixed arq.WorkerSettings import**
- **Found during:** Task 1 verification
- **Issue:** `from arq import WorkerSettings` failed - class doesn't exist in arq v0.27.0
- **Fix:** Created plain WorkerSettings class with class attributes instead of inheriting
- **Files modified:** backend/app/worker/settings.py

## Verification

- ✅ WorkerSettings imports and instantiates correctly
- ✅ PDF parser (pdf_parser.extract) imports correctly
- ✅ screen_resume task imports correctly
- ✅ Status transitions: pending→processing→completed/failed implemented
- ✅ Error message stored on failure
- ✅ Logging levels: DEBUG (job start), INFO (status changes), ERROR (failures)

## Run the Worker

```bash
cd backend
uv run arq app.worker.settings.WorkerSettings
```