from app.models.user import User
from app.models.team import Team
from app.models.task import Task, TaskStatus
from app.models.evaluation import Evaluation
from app.services.evaluation import get_average_score
from datetime import datetime


def test_average_score_no_evaluations(db_session):
    employee = User(email="avg1@example.com", password_hash="x", name="Employee")
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)

    result = get_average_score(db_session, employee.id)
    assert result is None

def test_average_score_multiple_evaluations(db_session):
    employee = User(email="avg2@example.com", password_hash="x", name="Employee2")
    manager = User(email="avg2mgr@example.com", password_hash="x", name="Manager2")
    db_session.add_all([employee, manager])
    db_session.commit()
    db_session.refresh(employee)
    db_session.refresh(manager)

    team = Team(name="Avg Team", invite_code="AVGCODE")
    db_session.add(team)
    db_session.commit()
    db_session.refresh(team)

    task1 = Task(title="Task 1", team_id=team.id, due_date=datetime(2026, 9, 1), assignee_id=employee.id, status=TaskStatus.DONE)
    task2 = Task(title="Task 2", team_id=team.id, due_date=datetime(2026, 9, 2), assignee_id=employee.id, status=TaskStatus.DONE)
    db_session.add_all([task1, task2])
    db_session.commit()
    db_session.refresh(task1)
    db_session.refresh(task2)

    db_session.add(Evaluation(task_id=task1.id, evaluator_id=manager.id, score=3))
    db_session.add(Evaluation(task_id=task2.id, evaluator_id=manager.id, score=5))
    db_session.commit()

    result = get_average_score(db_session, employee.id)
    assert result == 4.0