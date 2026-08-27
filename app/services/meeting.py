from sqlalchemy.orm import Session
from datetime import datetime
from app.models.meeting import Meeting, MeetingParticipant

def has_overlap(db: Session, user_id: int, new_starts_at: datetime, new_ends_at: datetime, exclude_meeting_id: int | None = None) -> bool:
    query = db.query(Meeting).join(MeetingParticipant, MeetingParticipant.meeting_id == Meeting.id).filter(MeetingParticipant.user_id == user_id)
    if exclude_meeting_id is not None:
        query = query.filter(Meeting.id != exclude_meeting_id)
    existing_meetings = query.all()
    for meeting in existing_meetings:
        if not (new_ends_at <= meeting.starts_at or new_starts_at >= meeting.ends_at):
            return True
    return False

