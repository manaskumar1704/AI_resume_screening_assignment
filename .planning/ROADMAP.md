# Roadmap: AI Resume Screening Service

## Project Overview
An async backend service that screens PDF resumes against Job Descriptions using an LLM.

---

## Phase 1: Project Scaffold & Database
**Goal:** Set up the project structure, Docker environment, and PostgreSQL schema with Alembic.

### Status
- [x] Complete

### Tasks
- Create docker-compose.yml with PostgreSQL, Redis, and API service
- Set up pyproject.toml with all Python dependencies
- Configure alembic.ini and create initial migration
- Create database.py with async SQLAlchemy engine and session factory
- Create models.py with the Evaluation table (status, resume_filename, jd_text, score, verdict, missing_requirements, justification, error_message, timestamps)
- Create .env.example with all required environment variables

### Success Criteria
- Docker containers start successfully
- Database migrations run without error
- Async engine connects to PostgreSQL

---

## Phase 2: Evaluate Endpoints
**Goal:** Build FastAPI endpoints for resume submission and status polling with ARQ queue integration.

### Tasks
- Create config.py with pydantic-settings for all env vars
- Create main.py FastAPI app factory
- Create schemas.py with Pydantic request/response models (EvalCreate, EvalResponse)
- Create POST /api/v1/evaluate endpoint (multipart/form-data: resume PDF, jd text)
- Create GET /api/v1/evaluate/{id} endpoint
- Integrate ARQ for background task queuing
- Validate PDF file type (reject non-PDF)
- Validate JD is not empty

### Success Criteria
- POST returns 202 with evaluation_id immediately
- GET returns current evaluation status
- Invalid requests return 422

---

## Phase 3: LLM Service
**Goal:** Create LangChain-based LLM service with external prompt and structured output.

### Tasks
- Create backend/prompts/resume_screening.md with system prompt
- Create llm_service.py that reads prompt at runtime
- Initialize provider-agnostic LLM (config.py drives model/provider)
- Implement ScorecardSchema for structured output
- Use .with_structured_output() for JSON parsing
- Log all LLM interactions

### Status
- [x] Task specs created: 03-TASK-SPECS.md
- [x] Plan created: 03-01-PLAN.md

### Plans
- [x] 03-01-PLAN.md — LLM Service Implementation (4 tasks)

### Success Criteria
- LLM returns structured JSON matching schema
- Prompt is external (not in Python code)
- Provider can be swapped via config

---

## Phase 4: ARQ Worker with Retry
**Goal:** Build background worker that processes evaluations with retry logic and DB persistence.

### Tasks
- Create worker/tasks.py with screen_resume task
- Implement PDF parsing (pdfplumber → plain text)
- Set up tenacity retry for rate limits (RateLimitError, APIConnectionError, HTTP 429)
- Configure exponential backoff, 3 attempts max
- Update evaluation status: pending → processing → completed/failed
- Write error_message on terminal failure

### Status
- [x] Task specs created: 04-TASK-SPECS.md
- [x] Plan created: 04-01-PLAN.md

### Plans
- [x] 04-01-PLAN.md — ARQ Worker Implementation (4 tasks)

### Success Criteria
- Worker picks up pending jobs
- Rate limits trigger retries
- Final state persisted to DB

---

## Phase 5: Integration Tests
**Goal:** Create pytest integration tests with mocked LLM covering full lifecycle.

### Tasks
- Create tests/conftest.py with test DB, test Redis, async client fixtures
- Create tests/fixtures/sample_resume.pdf
- Test: Upload valid PDF + JD → assert 202 + evaluation_id
- Test: Poll GET until completed → assert valid scorecard shape
- Test: Upload non-PDF → assert 422
- Test: LLM raises RateLimitError → assert retries → assert failed status
- Test: GET unknown ID → assert 404
- Clean up after each test (transactions or truncation)

### Success Criteria
- All 5 test cases pass
- LLM is never hit in tests

---

## Canonical References

- **AGENTS.md** — Source of truth for all implementation rules
- **DESIGN.md** — Frontend design system ("Dossier Framework")
- **backend/prompts/resume_screening.md** — LLM system prompt (must be external)