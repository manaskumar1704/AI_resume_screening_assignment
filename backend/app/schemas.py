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
    verdict: Optional[Literal["strong_match", "moderate_match", "weak_match"]] = None
    missing_requirements: Optional[List[str]] = None
    justification: Optional[str] = None

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
