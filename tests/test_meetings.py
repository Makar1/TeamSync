import pytest
from datetime import datetime
from app.models.user import User
from app.models.team import Team
from app.models.meeting import Meeting, MeetingParticipant
from app.services.meeting import has_overlap


@pytest.mark.parametrize("new_starts_at, new_ends_at, expected", [
    (datetime(2026, 9, 10, 9, 0), datetime(2026, 9, 10, 10, 0), False),
    (datetime(2026, 9, 10, 11, 0), datetime(2026, 9, 10, 12, 0), False),
    (datetime(2026, 9, 10, 10, 30), datetime(2026, 9, 10, 11, 30), True),
    (datetime(2026, 9, 10, 9, 30), datetime(2026, 9, 10, 11, 30), True),
])
def test_has_overlap(db_session, new_starts_at, new_ends_at, expected):
    user = User(email="overlap_test@example.com", password_hash="x", name="Overlap Test")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    team = Team(name="Overlap Team", invite_code="OVERLAPCODE")
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)

    existing_meeting = Meeting(
        title="Existing",
        team_id=team.id,
        starts_at=datetime(2026, 9, 10, 10, 0),
        ends_at=datetime(2026, 9, 10, 11, 0),
        organizer_id=user.id
    )
    db_session.add(existing_meeting)
    db_session.commit()
    db_session.refresh(existing_meeting)

    db_session.add(MeetingParticipant(meeting_id=existing_meeting.id, user_id=user.id))
    db_session.commit()

    result = has_overlap(db_session, user.id, new_starts_at, new_ends_at)
    assert result == expected