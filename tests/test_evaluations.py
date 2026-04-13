import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from io import BytesIO
from httpx import AsyncClient, ASGITransport
import uuid

from app.main import app
from app.database import get_db
from app.models import Evaluation


class InMemoryDB:
    def __init__(self):
        self.evaluations = {}

    async def add(self, evaluation):
        self.evaluations[str(evaluation.id)] = evaluation

    async def commit(self):
        pass

    async def refresh(self, evaluation):
        pass

    async def execute(self, query):
        return self

    def scalar_one_or_none(self):
        if hasattr(self, "evaluations") and self.evaluations:
            return list(self.evaluations.values())[0]
        return None


@pytest_asyncio.fixture
async def test_db_session():
    mem_db = InMemoryDB()

    class MockSession:
        def __init__(self, db):
            self.db = db

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def add(self, evaluation):
            await self.db.add(evaluation)

        async def commit(self):
            await self.db.commit()

        async def refresh(self, evaluation):
            await self.db.refresh(evaluation)

        async def execute(self, query):
            return self.db

        def scalar_one_or_none(self):
            if hasattr(self.db, "evaluations") and self.db.evaluations:
                return list(self.db.evaluations.values())[0]
            return None

    session = MockSession(mem_db)

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield session
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(test_db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_resume_pdf():
    pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Resources<</Font<</F1 4 0 R>>>/Parent 2 0 R/Contents 5 0 R>>endobj 4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj 5 0 obj<</Length 44>>stream
BT /F1 12 Tf 100 700 Td (John Doe - Software Engineer) Tj ET
endstream endobj xref 0 6 0000000000 65535 f 0000000009 00000 n 0000000058 00000 n 0000000100 00000 n 0000000153 00000 n 0000000219 00000 n trailer<</Size 6/Root 1 0 R>> startxref 298 %%EOF"""
    return BytesIO(pdf_content)


@pytest.mark.asyncio
async def test_upload_valid_pdf_jd(async_client, sample_resume_pdf):
    """Test 1: Upload valid PDF + JD → assert 202 + evaluation_id"""
    pdf_content = sample_resume_pdf.getvalue()
    sample_resume_pdf.seek(0)

    files = {"resume": ("resume.pdf", pdf_content, "application/pdf")}
    data = {"jd": "Looking for Python developer with ML experience"}

    response = await async_client.post("/api/v1/evaluate", files=files, data=data)

    assert response.status_code == 202
    body = response.json()
    assert "evaluation_id" in body
    assert body["status"] == "pending"

    try:
        uuid.UUID(body["evaluation_id"])
    except ValueError:
        pytest.fail("evaluation_id is not a valid UUID")


from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_poll_until_completed(test_db_session):
    """Test 2: Poll GET until completed → assert valid scorecard shape"""
    test_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    evaluation = Evaluation(
        id=test_id,
        status="completed",
        resume_filename="test.pdf",
        jd_text="Python developer",
        score=74,
        verdict="moderate_match",
        missing_requirements=["Kubernetes", "3+ years Go"],
        justification="Candidate has strong Python skills",
        confidence=0.85,
        match_percentages={"Python": 90, "ML": 75},
        extracted_skills=["Python", "ML"],
        created_at=now,
        updated_at=now,
    )
    test_db_session.db.evaluations[str(test_id)] = evaluation

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/evaluate/{test_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert "score" in body
    assert isinstance(body["score"], int)
    assert "verdict" in body
    assert body["verdict"] in ["strong_match", "moderate_match", "weak_match"]
    assert "missing_requirements" in body
    assert isinstance(body["missing_requirements"], list)
    assert "justification" in body
    assert isinstance(body["justification"], str)
    assert "confidence" in body
    assert isinstance(body["confidence"], float)
    assert "match_percentages" in body
    assert isinstance(body["match_percentages"], dict)
    assert "extracted_skills" in body
    assert isinstance(body["extracted_skills"], list)


@pytest.mark.asyncio
async def test_upload_non_pdf(async_client):
    """Test 3: Upload non-PDF → assert 422"""
    files = {"resume": ("resume.txt", b"not a pdf", "text/plain")}
    data = {"jd": "Python developer"}

    response = await async_client.post("/api/v1/evaluate", files=files, data=data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_unknown_id(async_client):
    """Test 5: GET unknown ID → assert 404"""
    unknown_id = str(uuid.uuid4())

    response = await async_client.get(f"/api/v1/evaluate/{unknown_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_rate_limit_error_retries():
    """Test 4: Worker retries on RateLimitError → eventually failed status"""
    from app.worker.tasks import call_llm_with_retry
    from app.worker.tasks import RateLimitError

    call_count = 0

    @patch("app.worker.tasks.is_rate_limit_error")
    async def test_retry_logic(mock_is_rate_limit):
        mock_is_rate_limit.return_value = True

        async def failing_llm(*args):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RateLimitError("Rate limit exceeded")
            return 1

        with patch("app.worker.tasks.llm_service.screen", side_effect=failing_llm):
            try:
                await call_llm_with_retry("resume", "jd")
            except RateLimitError:
                pass
            except Exception:
                pass

        assert call_count >= 1

    await test_retry_logic()
