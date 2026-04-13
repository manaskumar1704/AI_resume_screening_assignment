import base64
import logging
import time
import traceback
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from app.database import async_session_maker
from app.models import Evaluation
from app.services import llm_service, pdf_parser

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    pass


class InvalidLLMOutputError(Exception):
    """Raised when LLM output fails schema validation."""

    pass


class APIConnectionError(Exception):
    pass


def is_rate_limit_error(exception: BaseException) -> bool:
    error_msg = str(exception).lower()
    return (
        "rate limit" in error_msg
        or "429" in error_msg
        or "too many requests" in error_msg
        or isinstance(exception, (RateLimitError, APIConnectionError))
    )


def is_retryable_error(exception: BaseException) -> bool:
    """Check if error is retryable (rate limits, connection issues, invalid output)."""
    return is_rate_limit_error(exception) or isinstance(
        exception, InvalidLLMOutputError
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=30),
    retry=retry_if_exception_type(
        (RateLimitError, APIConnectionError, InvalidLLMOutputError)
    ),
    reraise=True,
)
async def call_llm_with_retry(resume_text: str, jd_text: str):
    start_time = time.time()
    try:
        scorecard = await llm_service.screen(resume_text, jd_text)

        if not scorecard or not scorecard.score:
            raise InvalidLLMOutputError("LLM returned empty or invalid scorecard")

        duration = time.time() - start_time
        logger.info(f"LLM call completed in {duration:.2f}s")
        return scorecard
    except Exception as e:
        duration = time.time() - start_time
        logger.warning(f"LLM call failed after {duration:.2f}s: {e}")
        if is_retryable_error(e):
            raise
        raise


async def screen_resume(
    ctx: dict,
    evaluation_id: str,
    resume_bytes_b64: str,
    jd_text: str,
):
    logger.info(f"Processing evaluation {evaluation_id}")

    resume_bytes = base64.b64decode(resume_bytes_b64)

    async with async_session_maker() as session:
        from sqlalchemy import select
        from sqlalchemy.dialects.postgresql import UUID

        result = await session.execute(
            select(Evaluation).where(Evaluation.id == evaluation_id)
        )
        evaluation = result.scalar_one_or_none()

        if not evaluation:
            logger.error(f"Evaluation {evaluation_id} not found")
            return {"status": "failed", "error": "Evaluation not found"}

        evaluation.status = "processing"
        await session.commit()
        logger.info(f"Evaluation {evaluation_id} set to processing")

        try:
            pdf_start = time.time()
            resume_text = await pdf_parser.extract(resume_bytes)
            pdf_duration = time.time() - pdf_start
            logger.info(
                f"PDF parsing completed in {pdf_duration:.2f}s for evaluation {evaluation_id}"
            )

            scorecard = await call_llm_with_retry(resume_text, jd_text)

            evaluation.status = "completed"
            evaluation.score = scorecard.score
            evaluation.verdict = scorecard.verdict
            evaluation.missing_requirements = scorecard.missing_requirements
            evaluation.justification = scorecard.justification
            evaluation.confidence = scorecard.confidence
            evaluation.match_percentages = scorecard.match_percentages
            evaluation.extracted_skills = scorecard.extracted_skills

            await session.commit()
            logger.info(
                f"Evaluation {evaluation_id} completed successfully with score {scorecard.score}"
            )
            return {"status": "completed", "evaluation_id": evaluation_id}

        except Exception as e:
            logger.error(f"Evaluation {evaluation_id} failed: {traceback.format_exc()}")

            evaluation.status = "failed"
            evaluation.error_message = str(e)[:500]
            await session.commit()

            return {"status": "failed", "error": str(e)[:500]}
