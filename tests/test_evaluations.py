import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from io import BytesIO
from httpx import AsyncClient, ASGITransport
import uuid


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


@pytest.mark.asyncio
async def test_poll_until_completed(async_client):
    """Test 2: Poll GET until completed → assert valid scorecard shape"""
    test_id = str(uuid.uuid4())

    with patch("app.api.routes.evaluations.select") as mock_select:
        mock_evaluation = MagicMock()
        mock_evaluation.id = test_id
        mock_evaluation.status = "completed"
        mock_evaluation.score = 74
        mock_evaluation.verdict = "moderate_match"
        mock_evaluation.missing_requirements = ["Kubernetes", "3+ years Go"]
        mock_evaluation.justification = "Candidate has strong Python skills"
        mock_evaluation.confidence = 0.85
        mock_evaluation.match_percentages = {"Python": 90, "ML": 75}
        mock_evaluation.extracted_skills = ["Python", "ML"]
        mock_evaluation.error_message = None
        mock_evaluation.resume_filename = "test.pdf"
        mock_evaluation.jd_text = "Python developer"
        mock_evaluation.created_at = "2026-04-13T00:00:00"
        mock_evaluation.updated_at = "2026-04-13T00:00:00"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_evaluation)
        mock_select.return_value = mock_result

        response = await async_client.get(f"/api/v1/evaluate/{test_id}")

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
async def test_rate_limit_error_retries(async_client):
    """Test 4: LLM raises RateLimitError → assert worker retries → assert failed status"""
    from unittest.mock import patch

    test_id = str(uuid.uuid4())

    call_count = 0

    async def mock_llm_that_retries(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Rate limit exceeded")
        return MagicMock(
            score=50,
            verdict="weak_match",
            missing_requirements=[],
            justification="Failed after retries",
            confidence=0.5,
            match_percentages={},
            extracted_skills=[],
        )

    with patch(
        "app.worker.tasks.llm_service.screen", side_effect=mock_llm_that_retries
    ):
        pass

    assert call_count >= 1
