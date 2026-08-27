from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Enum, UniqueConstraint
from datetime import datetime, timezone
import enum


class Meeting(Base):
    __tablename__ = 'meetings'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey('teams.id'), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    organizer_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc),nullable=False)

    organizer: Mapped['User'] = relationship()
    participants:  Mapped[list['MeetingParticipant']] = relationship(back_populates='meeting')


class MeetingParticipant(Base):
    __tablename__ = 'meeting_participants'

    __table_args__ = (UniqueConstraint('meeting_id', 'user_id'),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey('meetings.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    meeting: Mapped['Meeting'] = relationship(back_populates='participants')
    user: Mapped['User'] = relationship()