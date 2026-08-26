from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.models.task import TaskStatus

class TaskCreate(BaseModel):
    title: str = Field(min_length=5, max_length=100)
    description: str | None = None
    due_date: datetime
    assignee_id: int | None = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    team_id: int
    due_date: datetime
    status: TaskStatus
    assignee_id: int | None = None

    model_config = ConfigDict(from_attributes=True)

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=5, max_length=100)
    description: str | None = None
    assignee_id: int | None = None
    due_date: datetime | None = None

class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskCommentCreate(BaseModel):
    text: str

class TaskCommentResponse(BaseModel):
    id: int
    text: str
    task_id: int
    author_id: int
    created_at: datetime
