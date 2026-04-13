# AI Resume Screening Service

An async backend service that screens PDF resumes against job descriptions using an LLM. Resumes are uploaded via REST API, processed in the background by an ARQ worker, and scored against required skills with structured JSON output persisted to PostgreSQL.

## Overview

The system accepts PDF resumes and job descriptions via HTTP API, queues them for background processing, and returns structured evaluation scorecards including score, verdict, missing requirements, and confidence metrics.

**Async evaluation flow:**

1. Client uploads PDF resume + job description via `POST /api/v1/evaluate`
2. API validates input, checks for duplicate requests, stores pending record in PostgreSQL, enqueues task to Redis
3. ARQ worker picks up task, parses PDF with pdfplumber, calls LLM with LangChain
4. LLM returns structured JSON scorecard (never raw text parsing)
5. Worker updates database with results
6. Client polls `GET /api/v1/evaluate/{id}` for results

**Technologies:** FastAPI, ARQ (async Redis Queue), PostgreSQL 17, Redis 7, LangChain, Python 3.13

## Architecture Overview

```
Client → FastAPI API → PostgreSQL + Redis → ARQ Worker → LLM → DB update
```

**Client** submits resume via multipart/form-data POST. The API never calls the LLM directly.

**FastAPI API** validates input (PDF only, non-empty JD), checks for duplicate requests using request hash, inserts a `pending` row into PostgreSQL, and enqueues an ARQ task to Redis. Returns `202 Accepted` immediately with evaluation UUID.

**PostgreSQL** stores all evaluation state and results. Uses async SQLAlchemy 2.0 with asyncpg driver.

**Redis** serves as the ARQ queue. The worker connects as a consumer, ensuring reliable task pickup.

**ARQ Worker** processes tasks asynchronously. On pickup, it transitions status to `processing`. Parses PDF to plain text, calls the LLM with the job description and resume text, updates the row with the scorecard on success or `failed` status with error_message on terminal failure.

**LLM** is called via LangChain's `.with_structured_output()` for type-safe JSON. The worker uses tenacity for retry logic on rate limits and connection errors.

### Why Async Processing?

Resume screening involves I/O-bound operations (PDF parsing, LLM API calls) that would block request threads. By offloading to ARQ:

- API responds in milliseconds, not seconds
- LLM rate limits are handled gracefully with retries
- Multiple evaluations can process in parallel
- Workers scale independently from the API

### Separation of Concerns

The API layer handles only HTTP validation, storage, deduplication, and queueing. The worker handles all LLM interaction, PDF parsing, and database updates. This separation ensures:

- API stays responsive under load
- LLM failures don't crash the API
- Workers can be scaled horizontally

### Deduplication

The API computes a SHA-256 hash of the resume bytes + job description text. If a matching `request_hash` exists with status `completed`, the API returns the existing result instead of creating a duplicate evaluation.

## Tech Stack

### Backend

| Layer | Technology |
|-------|------------|
| Language | Python 3.13 |
| API | FastAPI 0.135.x |
| LLM Orchestration | LangChain 1.2.x |
| Async Worker | ARQ (async Redis Queue) |
| Database | PostgreSQL 17, async SQLAlchemy 2.0, asyncpg |
| Data Validation | Pydantic v2.12.x |
| Migrations | Alembic |
| PDF Parsing | pdfplumber |
| Retry Logic | tenacity |
| Queue/Cache | Redis 7-alpine |
| Package Manager | uv 0.11.x |
| Structured Logging | structlog |

### Infrastructure

| Layer | Technology |
|-------|------------|
| Container | Docker + docker-compose v2 |
| Testing | pytest + pytest-asyncio + httpx |

## System Design Decisions

### Why ARQ instead of Celery?

ARQ is async-native and integrates naturally with asyncio. Celery requires synchronous workers or additional complexity for async support. ARQ provides:

- Native asyncio coroutines
- Built-in retry with exponential backoff
- Health check endpoints
- Simple Redis-only dependencies (no message broker required)

### Why async SQLAlchemy?

Every operation in the request path is async:

- Database queries don't block the event loop
- Connection pool efficiently serves multiple concurrent requests
- Worker tasks are async coroutines

Synchronous drivers like psycopg2 would block threads, reducing throughput under load.

### Why structured LLM output?

The system uses LangChain's `.with_structured_output(ScorecardSchema)` to enforce JSON schema validation at the library level. This eliminates:

- Regex-based parsing that breaks on format variations
- Manual JSON extraction fallback logic in most cases
- Invalid response handling in the worker

If structured output fails, the worker attempts text parsing + JSON extraction as a fallback. Both failures trigger retry logic.

### Why external prompt files?

The LLM system prompt lives in `backend/prompts/resume_screening.md`, loaded at runtime. This ensures:

- Prompts don't require code changes to modify
- The prompt file is version-controlled separately
- Few-shot examples can be updated without redeploying

**Rule:** Never inline prompts in Python source. Always load with `open()` at runtime.

### Why structlog?

The project uses structlog for structured JSON logging in production, with console rendering in development. This enables:

- Correlation IDs in logs for request tracing
- Machine-parseable logs for production monitoring
- Human-readable logs in development

## Evaluation Lifecycle

1. **POST /api/v1/evaluate**
   - Content-Type: `multipart/form-data`
   - Fields: `resume` (PDF file), `jd` (string)
   - Response: `202 {"evaluation_id": "uuid", "status": "pending"}`
   - Validates PDF mime-type, rejects non-PDF with 422
   - Checks for duplicate requests using request_hash

2. **Duplicate Check** — If existing completed evaluation with same hash, returns existing result with note

3. **Pending** — Row inserted with `status='pending'`, task enqueued to Redis

4. **Worker pickup** — Sets `status='processing'`, parses PDF, calls LLM

5. **LLM processing** — Returns structured scorecard:
   - `score` (0-100)
   - `verdict` (strong_match | moderate_match | weak_match)
   - `missing_requirements` (list)
   - `justification` (text)
   - `confidence` (float)
   - `match_percentages` (dict)
   - `extracted_skills` (list)

6. **Success** — Worker updates row with scorecard, sets `status='completed'`

7. **Failure** — Worker sets `status='failed'`, writes `error_message`

8. **GET /api/v1/evaluate/{id}**
   - Pending: `{"id": "uuid", "status": "pending", "created_at": "..."}`
   - Completed: Full scorecard response
   - 404: Unknown ID

## Health & Monitoring

The API provides health check and metrics endpoints:

- **GET /health/live** — Liveness probe (returns 200 when process is running)
- **GET /health/ready** — Readiness probe (returns 200 when DB and Redis are reachable)
- **GET /metrics** — Prometheus-formatted metrics

## Setup Instructions (Docker)

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Add your GROQ_API_KEY (or OPENAI_API_KEY, ANTHROPIC_API_KEY)
# Edit .env and set the appropriate key

# 3. Start all services (API, worker, PostgreSQL, Redis)
docker-compose up --build

# 4. Access the API
# API runs at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## Running Migrations

Migrations run automatically on container startup via the startup event in `app/main.py`. To run manually:

```bash
docker-compose exec api uv run alembic upgrade head
```

To create a new migration after model changes:

```bash
docker-compose exec api uv run alembic revision --autogenerate -m "description"
```

## Testing Instructions

```bash
# Run all tests
docker-compose exec api pytest tests/ -v

# Run specific test file
docker-compose exec api pytest tests/test_evaluations.py -v
```

**Testing notes:**

- The LLM is always mocked in tests (never hits real API)
- Tests use a separate test database (`postgres_test`) with transaction rollback
- Only integration tests — no unit tests for individual functions
- 5 required test cases (see AGENTS.md Testing Rules)

## Failure Handling & Resilience

### Rate Limit Handling

Every LLM call is wrapped with tenacity retry logic:

- Retries on: `RateLimitError`, `APIConnectionError`, HTTP 429
- Strategy: exponential backoff, 3 attempts max
- On terminal failure: sets `status='failed'`, writes error_message to DB

### Worker Failures

Worker failures are not retried beyond the configured attempts. The final state is:

- `status='failed'`
- `error_message` contains the terminal error

Clients poll `GET /evaluate/{id}` to check for failure state.

### Structured Output Validation

If the LLM doesn't return valid JSON matching the schema:

1. First attempt: structured output validation
2. Fallback: text parse + JSON extraction
3. If fallback fails: treat as retryable error

Both failures trigger tenacity retry logic.

## Prompt Engineering Approach

The system prompt is stored in `backend/prompts/resume_screening.md`, loaded at runtime. It includes:

- Role definition (expert recruiter)
- Evaluation criteria
- Few-shot examples of input/output pairs
- Output schema instructions

The prompt is externalized to allow iteration without code changes. Any modifications to the prompt are version-controlled separately.

## Project Structure

```
resume-screener/
├── docker-compose.yml          # Full stack (api + worker + postgres + redis)
├── .env.example                # Environment template
├── README.md                   # This file
├── AGENTS.md                   # Project source of truth
├── DESIGN.md                   # Frontend design system ("Dossier Framework")
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml          # Python dependencies
│   ├── alembic.ini
│   ├── alembic/versions/       # Database migrations
│   │   ├── 001_initial.py
│   │   └── 002_add_request_hash.py
│   ├── prompts/               # External LLM prompts
│   │   └── resume_screening.md
│   └── app/
│       ├── main.py             # FastAPI app factory
│       ├── config.py           # Pydantic settings with validation
│       ├── database.py        # Async SQLAlchemy engine
│       ├── models.py          # SQLAlchemy ORM models
│       ├── schemas.py         # Pydantic request/response
│       ├── api/routes/         # API endpoints
│       │   ├── evaluations.py # POST/GET evaluation endpoints
│       │   ├── health.py      # Health check endpoints
│       │   └── metrics.py     # Prometheus metrics
│       ├── services/          # PDF parser, LLM service
│       └── worker/             # ARQ tasks and settings
│
├── tests/                     # Integration tests
│   ├── conftest.py
│   ├── test_evaluations.py
│   └── fixtures/
│       └── sample_resume.pdf
│
└── frontend/               # Next.js 15 (bonus, non-blocking)
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# LLM Provider (openai | anthropic | groq)
LLM_PROVIDER=groq
LLM_MODEL=gpt-4o-mini

# API Key for your provider
GROQ_API_KEY=

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/resume_screener

# Redis
REDIS_URL=redis://redis:6379

# App
DEBUG=false
```

**No API keys are committed.** Always use `.env` for secrets.

## Configuration Validation

The application validates configuration at startup:

- DATABASE_URL and REDIS_URL must be non-empty
- LLM_PROVIDER must be one of: openai, anthropic, groq
- Provider-specific API key must be set (GROQ_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY)

If any required configuration is missing, the application fails fast with a clear error message.

## Notes for Evaluators

- **No API keys committed** — All keys go in `.env`, which is gitignored
- **Recent fixes** — Production audit addressed: duplicate endpoint handlers removed, API response schema fields completed
- **System requires an API key** — Set `GROQ_API_KEY` (or `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) in `.env`
- **Full stack runs in Docker** — `docker-compose up --build` starts everything
- **Tests don't require real LLM** — The LLM is mocked in all tests
- **Async architecture** — API never calls LLM directly; ARQ worker handles all LLM interaction
- **Deduplication** — Duplicate requests (same resume + JD) return existing results
- **Health checks** — Use `/health/live` and `/health/ready` for container orchestration
- **Metrics** — Prometheus metrics available at `/metrics`