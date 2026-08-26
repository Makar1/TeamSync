from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Enum
from datetime import datetime, timezone
import enum


class TaskStatus(str, enum.Enum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] =  mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=True)
    team_id: Mapped[int] = mapped_column(ForeignKey('teams.id'), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), nullable=False,default=TaskStatus.OPEN)

    comments: Mapped[list['TaskComment']] = relationship(back_populates='task')
    assignee: Mapped['User'] = relationship()


class TaskComment(Base):
    __tablename__ = 'task_comments'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'), nullable=False)
    text: Mapped[str] = mapped_column(String(2000))
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    author: Mapped['User'] = relationship()
    task: Mapped['Task'] = relationship(back_populates='comments')