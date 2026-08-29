from fastapi import APIRouter, Depends,HTTPException, status
from sqlalchemy.orm import Session
from app.models.meeting import Meeting, MeetingParticipant
from app.schemas.meeting import  MeetingCreate, MeetingResponse, MeetingUpdate
from app.services.meeting import has_overlap
from app.dependencies import get_team_membership
from app.models.team_member import TeamMember
from app.models.team_member import TeamRole
from app.db.session import get_db


meetings_router = APIRouter(prefix='/teams/{team_id}/meetings', tags=['meetings'])
@meetings_router.post('/',response_model=MeetingResponse)
def create_meeting(meeting_data: MeetingCreate, db: Session = Depends(get_db), membership: TeamMember = Depends(get_team_membership)):
    participant_ids = set(meeting_data.participant_ids) | {membership.user_id}
    for pid in participant_ids:
        if has_overlap(db, pid, meeting_data.starts_at, meeting_data.ends_at):
            raise HTTPException(status_code=409, detail=f"Участник {pid} занят в это время")
    meeting = Meeting(
        title=meeting_data.title,
        team_id=membership.team_id,
        starts_at=meeting_data.starts_at,
        ends_at=meeting_data.ends_at,
        organizer_id=membership.user_id
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    for pid in participant_ids:
        db.add(MeetingParticipant(meeting_id=meeting.id, user_id=pid))
    db.commit()

    return MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        team_id=meeting.team_id,
        starts_at=meeting.starts_at,
        ends_at=meeting.ends_at,
        organizer_id=meeting.organizer_id,
        created_at=meeting.created_at,
        participant_ids=list(participant_ids)
    )

@meetings_router.patch('/{meeting_id}',response_model=MeetingResponse)
def update_meeting(meeting_id: int,meeting_data: MeetingUpdate, db: Session = Depends(get_db), membership: TeamMember = Depends(get_team_membership)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.team_id == membership.team_id).first()
    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="Нет такой встречи"
        )
    if not (membership.role == TeamRole.MANAGER or meeting.organizer_id == membership.user_id):
        raise HTTPException(
            status_code=403,
            detail="Только менеджер или организатор может менять встречу"
        )
    new_starts_at = meeting_data.starts_at if meeting_data.starts_at is not None else meeting.starts_at
    new_ends_at = meeting_data.ends_at if meeting_data.ends_at is not None else meeting.ends_at
    if new_ends_at <= new_starts_at:
        raise HTTPException(
            400,
            "ends_at должен быть позже starts_at"
        )
    if meeting_data.participant_ids is not None:
        new_participant_ids = set(meeting_data.participant_ids) | {meeting.organizer_id}
    else:
        new_participant_ids = {mp.user_id for mp in meeting.participants}
    for pid in new_participant_ids:
        if has_overlap(db, pid, new_starts_at, new_ends_at, exclude_meeting_id=meeting.id):
            raise HTTPException(409, f"Участник {pid} занят в это время")
    if meeting_data.title is not None:
        meeting.title = meeting_data.title
    meeting.starts_at = new_starts_at
    meeting.ends_at = new_ends_at
    if meeting_data.participant_ids is not None:
        db.query(MeetingParticipant).filter(MeetingParticipant.meeting_id == meeting.id).delete()
        for pid in new_participant_ids:
            db.add(MeetingParticipant(meeting_id=meeting.id, user_id=pid))
    db.commit()
    db.refresh(meeting)
    return MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        team_id=meeting.team_id,
        starts_at=meeting.starts_at,
        ends_at=meeting.ends_at,
        organizer_id=meeting.organizer_id,
        created_at=meeting.created_at,
        participant_ids=list(new_participant_ids)
    )

@meetings_router.delete('/{meeting_id}',response_model=MeetingResponse)
def delete_meeting(meeting_id: int, db: Session = Depends(get_db), membership: TeamMember = Depends(get_team_membership)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.team_id == membership.team_id).first()
    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="Нет такой встречи"
        )
    if not (membership.role == TeamRole.MANAGER or meeting.organizer_id == membership.user_id):
        raise HTTPException(
            status_code=403,
            detail="Только менеджер или организатор может удалять встречу"
        )
    participant_ids = [mp.user_id for mp in meeting.participants]
    db.query(MeetingParticipant).filter(MeetingParticipant.meeting_id == meeting.id).delete()
    db.delete(meeting)
    db.commit()
    return MeetingResponse(
        id=meeting.id,
        title=meeting.title,
        team_id=meeting.team_id,
        starts_at=meeting.starts_at,
        ends_at=meeting.ends_at,
        organizer_id=meeting.organizer_id,
        created_at=meeting.created_at,
        participant_ids=participant_ids
    )

@meetings_router.get('', response_model=list[MeetingResponse])
def list_meetings(db: Session = Depends(get_db), membership: TeamMember = Depends(get_team_membership)):
    meetings_raw = db.query(Meeting).filter(Meeting.team_id == membership.team_id).all()
    return [
        MeetingResponse(
            id=m.id, title=m.title, team_id=m.team_id,
            starts_at=m.starts_at, ends_at=m.ends_at,
            organizer_id=m.organizer_id, created_at=m.created_at,
            participant_ids=[p.user_id for p in m.participants]
        )
        for m in meetings_raw
    ]