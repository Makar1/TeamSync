from pydantic import BaseModel, Field, ConfigDict, model_validator
from datetime import datetime

class MeetingCreate(BaseModel):
    title: str
    starts_at: datetime
    ends_at: datetime
    participant_ids: list[int]

    @model_validator(mode='after')
    def check_time_order(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at должен быть позже starts_at")
        return self

class MeetingResponse(BaseModel):
    id: int
    title: str
    team_id: int
    starts_at: datetime
    ends_at: datetime
    organizer_id: int
    created_at: datetime
    participant_ids: list[int]

    model_config = ConfigDict(from_attributes=True)



class MeetingUpdate(BaseModel):
    title: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    participant_ids: list[int] | None = None
