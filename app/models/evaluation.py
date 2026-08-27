from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Enum
from datetime import datetime, timezone


class Evaluation(Base):

    __tablename__ = 'evaluations'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'), nullable=False, unique=True)
    evaluator_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    score: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    task: Mapped['Task'] = relationship()
    evaluator: Mapped['User'] = relationship()