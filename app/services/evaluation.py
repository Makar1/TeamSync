from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.task import Task
from app.models.evaluation import Evaluation

def get_average_score(db: Session, user_id: int) -> float | None:
    return db.query(func.avg(Evaluation.score)).join(Task, Evaluation.task_id == Task.id).filter(Task.assignee_id == user_id).scalar()