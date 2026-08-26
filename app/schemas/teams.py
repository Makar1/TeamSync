from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.team_member import TeamRole

class TeamCreate(BaseModel):
    name: str = Field(min_length=5, max_length=100)

class TeamResponse(BaseModel):
    id: int
    name: str = Field(min_length=5, max_length=100)
    invite_code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TeamJoin(BaseModel):
    invite_code: str

class TeamMemberResponse(BaseModel):
    id: int
    name: str
    role: TeamRole

    model_config = ConfigDict(from_attributes=True)

