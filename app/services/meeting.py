from sqlalchemy.orm import Session
from datetime import datetime
from app.models.meeting import Meeting, MeetingParticipant

class InvalidTimeRangeError(ValueError):
    pass

class MeetingConflictError(ValueError):
    pass

def has_overlap(db: Session, user_id: int, new_starts_at: datetime, new_ends_at: datetime, exclude_meeting_id: int | None = None) -> bool:
    query = db.query(Meeting).join(MeetingParticipant, MeetingParticipant.meeting_id == Meeting.id).filter(MeetingParticipant.user_id == user_id)
    if exclude_meeting_id is not None:
        query = query.filter(Meeting.id != exclude_meeting_id)
    existing_meetings = query.all()
    for meeting in existing_meetings:
        if not (new_ends_at <= meeting.starts_at or new_starts_at >= meeting.ends_at):
            return True
    return False

def update_meeting_with_participants(db: Session, meeting: Meeting, title: str | None, starts_at: datetime | None, ends_at: datetime | None, participant_ids: set[int] | None) -> Meeting:
    new_starts_at = starts_at if starts_at is not None else meeting.starts_at
    new_ends_at = ends_at if ends_at is not None else meeting.ends_at
    if new_ends_at <= new_starts_at:
        raise InvalidTimeRangeError("ends_at должен быть позже starts_at")

    if participant_ids is not None:
        new_participant_ids = participant_ids | {meeting.organizer_id}
    else:
        new_participant_ids = {mp.user_id for mp in meeting.participants}

    for pid in new_participant_ids:
        if has_overlap(db, pid, new_starts_at, new_ends_at, exclude_meeting_id=meeting.id):
            raise MeetingConflictError(f"Участник {pid} занят в это время")

    if title is not None:
        meeting.title = title
    meeting.starts_at = new_starts_at
    meeting.ends_at = new_ends_at

    if participant_ids is not None:
        db.query(MeetingParticipant).filter(MeetingParticipant.meeting_id == meeting.id).delete()
        for pid in new_participant_ids:
            db.add(MeetingParticipant(meeting_id=meeting.id, user_id=pid))

    db.commit()
    db.refresh(meeting)
    return new_participant_ids
