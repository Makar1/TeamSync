from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.task import Task
from app.models.evaluation import Evaluation
from app.models.task import Task, TaskStatus

def get_average_score(db: Session, user_id: int) -> float | None:
    return db.query(func.avg(Evaluation.score)).join(Task, Evaluation.task_id == Task.id).filter(Task.assignee_id == user_id).scalar()

class TaskNotEvaluableError(ValueError):
    pass

class AlreadyEvaluatedError(ValueError):
    pass


def create_evaluation_for_task(db: Session, task: Task, evaluator_id: int, score: int, comment: str | None) -> Evaluation:
    if task.status != TaskStatus.DONE:
        raise TaskNotEvaluableError("Оценивать можно только задачи в статусе done")
    if task.assignee_id is None:
        raise TaskNotEvaluableError("У задачи нет исполнителя")

    existing = db.query(Evaluation).filter(Evaluation.task_id == task.id).first()
    if existing is not None:
        raise AlreadyEvaluatedError("Эта задача уже оценена")

    evaluation = Evaluation(task_id=task.id, evaluator_id=evaluator_id, score=score, comment=comment)
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation