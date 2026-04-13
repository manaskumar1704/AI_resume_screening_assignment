import base64
import uuid
import logging
import hashlib
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, status

from app.config import settings
from app.schemas import EvalResponse
from app.database import get_db
from app.models import Evaluation
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
logger = logging.getLogger(__name__)


def compute_request_hash(resume_bytes: bytes, jd_text: str) -> str:
    """Compute hash of resume + JD for deduplication."""
    combined = resume_bytes + jd_text.encode("utf-8")
    return hashlib.sha256(combined).hexdigest()


async def create_evaluation(
    resume: UploadFile,
    jd: str,
    resume_bytes: bytes,
    db: AsyncSession,
) -> tuple[Evaluation, bool]:
    """
    Create a new evaluation or return existing if duplicate.
    Returns (evaluation, is_duplicate).
    """
    if resume.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File must be a PDF",
        )

    if not jd or not jd.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Job description cannot be empty",
        )

    if len(resume_bytes) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB",
        )

    request_hash = compute_request_hash(resume_bytes, jd)

    existing = await db.execute(
        select(Evaluation).where(
            and_(
                Evaluation.request_hash == request_hash,
                Evaluation.status == "completed",
            )
        )
    )
    existing_eval = existing.scalar_one_or_none()

    if existing_eval:
        logger.info(
            f"Returning existing evaluation for duplicate request: {existing_eval.id}"
        )
        return existing_eval, True

    eval_id = uuid.uuid4()
    evaluation = Evaluation(
        id=eval_id,
        status="pending",
        resume_filename=resume.filename,
        jd_text=jd,
        request_hash=request_hash,
    )
    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)

    return evaluation, False


@router.post("/evaluate", status_code=status.HTTP_202_ACCEPTED)
async def evaluate_resume(
    resume: UploadFile = File(...),
    jd: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"POST /evaluate request received for file: {resume.filename}")
    try:
        resume_bytes = await resume.read()
        evaluation, is_duplicate = await create_evaluation(resume, jd, resume_bytes, db)

        if is_duplicate:
            return {
                "evaluation_id": str(evaluation.id),
                "status": evaluation.status,
                "note": "returned existing",
            }

        resume_b64 = base64.b64encode(resume_bytes).decode()

        try:
            from arq import create_pool
            from arq.connections import RedisSettings

            redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
            pool = await create_pool(redis_settings)
            await pool.enqueue_job(
                "app.worker.tasks.screen_resume",
                evaluation_id=str(evaluation.id),
                resume_bytes_b64=resume_b64,
                jd_text=jd,
                _queue_name="arq:queue",
            )
            await pool.close()
            logger.info(f"Job enqueued for evaluation {evaluation.id}")
        except Exception as e:
            logger.error(f"Failed to enqueue job: {e}")

        return {"evaluation_id": str(evaluation.id), "status": "pending"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Evaluation creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create evaluation",
        )


@router.get("/evaluate/{evaluation_id}")
async def get_evaluation(
    evaluation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Evaluation).where(Evaluation.id == evaluation_id))
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found"
        )

    return EvalResponse(
        id=evaluation.id,
        status=evaluation.status,
        score=evaluation.score,
        verdict=evaluation.verdict,
        missing_requirements=evaluation.missing_requirements,
        justification=evaluation.justification,
        confidence=evaluation.confidence,
        match_percentages=evaluation.match_percentages,
        extracted_skills=evaluation.extracted_skills,
        error_message=evaluation.error_message,
        resume_filename=evaluation.resume_filename,
        jd_text=evaluation.jd_text,
        created_at=evaluation.created_at,
        updated_at=evaluation.updated_at,
    )
