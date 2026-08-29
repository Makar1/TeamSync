from fastapi import APIRouter, Depends,HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from fastapi import Query
from app.models.task import Task
from datetime import datetime
from app.models.meeting import Meeting, MeetingParticipant
from app.schemas.meeting import   MeetingResponse
from app.dependencies import   get_current_user

from app.db.session import get_db

from app.schemas.calendar import CalendarResponse


calendar_router = APIRouter(prefix='/calendar', tags=['calendar'])
@calendar_router.get('', response_model=CalendarResponse)
def get_calendar(from_: datetime = Query(..., alias="from"), to: datetime = Query(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.assignee_id == current_user.id, Task.due_date >= from_,
                                  Task.due_date <= to).all()
    meetings_raw = db.query(Meeting).join(MeetingParticipant, MeetingParticipant.meeting_id == Meeting.id).filter(
        MeetingParticipant.user_id == current_user.id, Meeting.starts_at >= from_, Meeting.starts_at <= to).all()

    meetings = [
        MeetingResponse(
            id=m.id, title=m.title, team_id=m.team_id,
            starts_at=m.starts_at, ends_at=m.ends_at,
            organizer_id=m.organizer_id, created_at=m.created_at,
            participant_ids=[p.user_id for p in m.participants]
        )
        for m in meetings_raw
    ]
    return CalendarResponse(tasks=tasks, meetings=meetings)