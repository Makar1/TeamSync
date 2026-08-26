from fastapi import APIRouter, Depends,HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User

from app.models.team_member import TeamRole
from app.models.team import Team
from app.models.team_member import TeamMember
from app.schemas.teams import  TeamMemberResponse, TeamJoin, TeamResponse, TeamCreate
from app.dependencies import  generate_invite_code, get_current_user, get_team_membership
from  app.db.session import get_db


router= APIRouter(prefix='/teams', tags=['teams'])
@router.post('/', response_model=TeamResponse)
def create_team(new_team:TeamCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invite_code = generate_invite_code()

    team = Team(
        name=new_team.name,
        invite_code=invite_code
    )
    db.add(team)
    db.commit()
    db.refresh(team)

    head_team = TeamMember(
        team_id = team.id,
        user_id = current_user.id,
        role = TeamRole.MANAGER
    )
    db.add(head_team)
    db.commit()

    return team

@router.post('/{team_id}/join', response_model=TeamResponse)
def join_team(team_id: int, join_data: TeamJoin, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Нет такой команды",
        )
    if join_data.invite_code != team.invite_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный invite_code",
        )

    existing = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже состоите в этой команд",
        )

    membership = TeamMember(
        team_id=team_id,
        user_id=current_user.id,
        role=TeamRole.MEMBER
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return team

@router.get('/{team_id}/members/', response_model= list[TeamMemberResponse])
def list_team_membership(team_id: int, db: Session = Depends(get_db), membership: TeamMember = Depends(get_team_membership)):
    team = db.query(Team).filter(Team.id == team_id).first()
    result = [TeamMemberResponse(id=m.id, name=m.user.name, role=m.role) for m in team.members]
    return result



