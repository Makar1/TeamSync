from pydantic import BaseModel
from app.schemas.task import TaskResponse
from app.schemas.meeting import MeetingResponse

class CalendarResponse(BaseModel):
    tasks: list[TaskResponse]
    meetings: list[MeetingResponse]