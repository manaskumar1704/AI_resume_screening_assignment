from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Literal
from datetime import datetime
from uuid import UUID


class EvalCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class EvalResponse(BaseModel):
    id: UUID
    status: Literal["pending", "processing", "completed", "failed"]
    score: Optional[int] = None
    verdict: Optional[str] = None
    missing_requirements: Optional[List[str]] = None
    justification: Optional[str] = None
    confidence: Optional[float] = None
    match_percentages: Optional[Dict[str, float]] = None
    extracted_skills: Optional[List[str]] = None
    error_message: Optional[str] = None
    resume_filename: str
    jd_text: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvaluationStatus(BaseModel):
    id: UUID
    status: Literal["pending", "processing", "completed", "failed"]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
