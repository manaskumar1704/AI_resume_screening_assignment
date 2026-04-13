import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from io import BytesIO
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database import async_session_maker


@pytest.fixture
async def mock_llm():
    """Mock LLM to return structured scorecard"""
    mock = AsyncMock()
    mock_score = MagicMock()
    mock_score.score = 74
    mock_score.verdict = "moderate_match"
    mock_score.missing_requirements = ["Kubernetes", "3+ years Go"]
    mock_score.justification = (
        "Candidate has strong Python and ML skills but lacks required experience."
    )
    mock_score.confidence = 0.85
    mock_score.match_percentages = {"Python": 90, "ML": 75, "Kubernetes": 20}
    mock_score.extracted_skills = ["Python", "Machine Learning", "SQL"]

    mock.with_structured_output = MagicMock(return_value=mock)
    mock.ainvoke = AsyncMock(return_value=mock_score)

    return mock


@pytest.fixture
async def mock_arq():
    """Mock ARQ enqueue"""
    mock = AsyncMock()
    mock.enqueue_job = AsyncMock(return_value=MagicMock(job_id="test-job-id"))
    mock.close = AsyncMock()
    return mock


@pytest_asyncio.fixture
async def test_db():
    """Async SQLAlchemy session with transaction rollback"""
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def async_client(mock_llm, mock_arq):
    """httpx.AsyncClient for FastAPI test client"""

    with patch("app.api.routes.evaluations.get_llm") as mock_get_llm:
        mock_get_llm.return_value = mock_llm

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


@pytest.fixture
def sample_resume_pdf():
    """Get sample PDF bytes for upload"""
    pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Resources<</Font<</F1 4 0 R>>>/Parent 2 0 R/Contents 5 0 R>>endobj 4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj 5 0 obj<</Length 44>>stream
BT /F1 12 Tf 100 700 Td (John Doe - Software Engineer) Tj ET
endstream endobj xref 0 6 0000000000 65535 f 0000000009 00000 n 0000000058 00000 n 0000000100 00000 n 0000000153 00000 n 0000000219 00000 n trailer<</Size 6/Root 1 0 R>> startxref 298 %%EOF"""
    return BytesIO(pdf_content)
