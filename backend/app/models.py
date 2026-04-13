import uuid
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(String(20), nullable=False, default="pending")
    resume_filename = Column(Text, nullable=False)
    jd_text = Column(Text, nullable=False)
    request_hash = Column(String(64), nullable=True, index=True)
    score = Column(Integer, nullable=True)
    verdict = Column(String(50), nullable=True)
    missing_requirements = Column(JSONB, nullable=True)
    justification = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    match_percentages = Column(JSONB, nullable=True)
    extracted_skills = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (Index("ix_evaluations_hash_status", "request_hash", "status"),)
