from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import  UserResponse
from app.dependencies import get_current_user
from sqlalchemy import func
from  app.db.session import get_db
from app.models.task import Task
from app.models.evaluation import Evaluation
from app.schemas.evaluation import MyEvaluationsResponse

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/me', response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.get('/me/evaluations', response_model=MyEvaluationsResponse)
def get_my_evaluations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    evaluations = db.query(Evaluation).join(Task, Evaluation.task_id == Task.id).filter(Task.assignee_id == current_user.id).all()
    average_score = db.query(func.avg(Evaluation.score)).join(Task, Evaluation.task_id == Task.id).filter(Task.assignee_id == current_user.id).scalar()
    return MyEvaluationsResponse(evaluations=evaluations, average_score=average_score)