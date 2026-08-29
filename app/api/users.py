from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import  UserResponse
from app.dependencies import get_current_user
from sqlalchemy import func
from  app.db.session import get_db
from app.models.task import Task
from app.models.evaluation import Evaluation
from app.schemas.evaluation import MyEvaluationsResponse
from app.services.evaluation import get_average_score
from app.core.security import verify_password, get_password_hash
from app.schemas.user import PasswordChange

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/me', response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.get('/me/evaluations', response_model=MyEvaluationsResponse)
def get_my_evaluations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    evaluations = db.query(Evaluation).join(Task, Evaluation.task_id == Task.id).filter(Task.assignee_id == current_user.id).all()
    average_score = get_average_score(db, current_user.id)
    return MyEvaluationsResponse(evaluations=evaluations, average_score=average_score)

@router.patch('/me/password')
def change_password(password_data: PasswordChange, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный текущий пароль")
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    return {"detail": "Пароль успешно изменён"}