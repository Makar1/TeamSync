from fastapi import APIRouter, Depends,HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User

from app.models.team_member import TeamRole
from app.models.task import Task, TaskComment, TaskStatus

from app.models.team_member import TeamMember
from app.schemas.teams import  TeamMemberResponse, TeamJoin, TeamResponse, TeamCreate

from app.dependencies import  generate_invite_code, get_current_user, get_team_membership
from  app.db.session import get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate, TaskStatusUpdate, TaskCommentCreate, TaskCommentResponse
from app.schemas.evaluation import  EvaluationCreate, EvaluationResponse, MyEvaluationsResponse
from app.models.evaluation import Evaluation


tasks_router = APIRouter(prefix='/teams/{team_id}/tasks', tags=['tasks'])
@tasks_router.post('',response_model=TaskResponse)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db), membership: TeamMember = Depends(get_team_membership)):

    if not membership.role == TeamRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджер команды может создавать задачи"
        )

    task = Task(
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        assignee_id=task_data.assignee_id,
        team_id=membership.team_id
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return task

@tasks_router.get('', response_model=list[TaskResponse])
def list_task(team_id: int,db: Session = Depends(get_db), membership: TeamMember = Depends(get_team_membership)):

    tasks = db.query(Task).filter(Task.team_id == team_id).all()
    return tasks

@tasks_router.patch('/{task_id}', response_model=TaskResponse)
def update_task(task_id: int ,task_data: TaskUpdate, db: Session = Depends(get_db), membership: TeamMember = Depends(get_team_membership)):
    if not membership.role == TeamRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджер команды может создавать задачи"
        )
    task = db.query(Task).filter(Task.id == task_id, Task.team_id == membership.team_id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Нет такой задачи")

    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.assignee_id is not None:
        task.assignee_id = task_data.assignee_id
    if task_data.due_date is not None:
        task.due_date = task_data.due_date

    db.commit()
    db.refresh(task)
    return task

@tasks_router.delete('/{task_id}',response_model=TaskResponse)
def delete_task(task_id: int,db: Session = Depends(get_db), membership: TeamMember = Depends(get_team_membership)):
    if not membership.role == TeamRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджер команды может создавать задачи"
        )
    task = db.query(Task).filter(Task.id == task_id, Task.team_id == membership.team_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Нет такой задачи"
        )

    db.delete(task)
    db.commit()
    return task

@tasks_router.patch('/{task_id}/status', response_model=TaskResponse)
def update_task_status(task_id: int, status_data: TaskStatusUpdate, db: Session = Depends(get_db), membership: TeamMember = Depends(get_team_membership)):
    task = db.query(Task).filter(Task.id == task_id, Task.team_id == membership.team_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Нет такой задачи"
        )
    if not (membership.role == TeamRole.MANAGER or task.assignee_id == membership.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="вам запрещено менять статус задачи"
        )

    task.status = status_data.status
    db.commit()
    db.refresh(task)
    return task


comments_router = APIRouter(prefix='/tasks', tags=['tasks'])
@comments_router.post('/{task_id}/comments', response_model=TaskCommentResponse)
def create_comment(task_id: int, comment_data: TaskCommentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Нет такой задачи"
        )
    membership = db.query(TeamMember).filter(TeamMember.team_id == task.team_id, TeamMember.user_id == user.id).first()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="вам запрещено "
        )
    comment = TaskComment(task_id=task_id, author_id=user.id, text=comment_data.text)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


evaluations_router = APIRouter(prefix='/tasks', tags=['evaluations'])
@evaluations_router.post('/{task_id}/evaluation',response_model=EvaluationResponse)
def create_evaluation(task_id: int, eval_data: EvaluationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(404, "Нет такой задачи")
    membership = db.query(TeamMember).filter(TeamMember.team_id == task.team_id, TeamMember.user_id == current_user.id).first()
    if membership is None:
        raise HTTPException(403, "Вы не состоите в этой команде")
    if membership.role != TeamRole.MANAGER:
        raise HTTPException(403, "Только менеджер может оценивать задачи")
    if task.status != TaskStatus.DONE:
        raise HTTPException(400, "Оценивать можно только задачи в статусе done")
    if task.assignee_id is None:
        raise HTTPException(400, "У задачи нет исполнителя")
    existing = db.query(Evaluation).filter(Evaluation.task_id == task_id).first()
    if existing is not None:
        raise HTTPException(409, "Эта задача уже оценена")
    evaluation = Evaluation(task_id=task_id, evaluator_id=current_user.id, score=eval_data.score,
                            comment=eval_data.comment)
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation
