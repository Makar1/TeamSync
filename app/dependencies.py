from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.team_member import TeamMember
from jose import JWTError, jwt
from app.core.config import settings
import secrets

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Невалидный токен", headers={"WWW-Authenticate": "Bearer"})

    current_email = payload.get("sub")
    current_user = db.query(User).filter(User.email == current_email).first()
    if current_user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден", headers={"WWW-Authenticate": "Bearer"})

    return current_user


def generate_invite_code():
    invite_code = secrets.token_urlsafe(8)
    return invite_code

def get_team_membership(team_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    membership = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == current_user.id).first()
    if membership is None:
        raise HTTPException(status_code=403, detail="Вы не состоите в этой команде")
    return membership
