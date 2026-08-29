from pydantic import BaseModel, Field, ConfigDict, model_validator
from datetime import datetime

class EvaluationCreate(BaseModel):
    score: int = Field(ge=1, le=5)
    comment: str | None = None


class EvaluationResponse(BaseModel):
    id: int
    task_id: int
    evaluator_id: int
    score: int
    comment: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MyEvaluationsResponse(BaseModel):
    evaluations: list[EvaluationResponse]
    average_score: float | None