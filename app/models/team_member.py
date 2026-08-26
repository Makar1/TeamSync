from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum


from app.db.base import Base

class TeamRole(str, enum.Enum):
    MANAGER = 'manager'
    MEMBER = 'member'



class TeamMember(Base):
    __tablename__ = "team_members"

    __table_args__ = (UniqueConstraint('user_id', 'team_id'),)

    id: Mapped[int] = mapped_column( primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(ForeignKey('teams.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    role: Mapped[TeamRole] = mapped_column(Enum(TeamRole), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    team: Mapped['Team'] = relationship(back_populates='members')
    user: Mapped['User'] = relationship(back_populates='team_memberships')