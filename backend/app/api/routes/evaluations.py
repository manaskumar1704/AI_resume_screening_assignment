import base64
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, status

from app.config import settings
from app.schemas import EvalResponse
from app.database import get_db
from app.models import Evaluation
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
logger = logging.getLogger(__name__)


async def create_evaluation(
    resume: UploadFile,
    jd: str,
    db: AsyncSession,
) -> Evaluation:
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

    resume_bytes = await resume.read()
    if len(resume_bytes) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB",
        )

    eval_id = uuid.uuid4()
    evaluation = Evaluation(
        id=eval_id,
        status="pending",
        resume_filename=resume.filename,
        jd_text=jd,
    )
    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)

    return evaluation


@router.post("/evaluate", status_code=status.HTTP_202_ACCEPTED)
async def evaluate_resume(
    resume: UploadFile = File(...),
    jd: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        evaluation = await create_evaluation(resume, jd, db)

        resume_bytes = await resume.read()
        resume_b64 = base64.b64encode(resume_bytes).decode()

        try:
            from arq import create_pool
            from arq.connections import RedisSettings

            redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
            pool = await create_pool(redis_settings)
            await pool.enqueue_job(
                "screen_resume",
                evaluation_id=str(evaluation.id),
                resume_bytes=resume_b64,
                jd_text=jd,
            )
            await pool.close()
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
