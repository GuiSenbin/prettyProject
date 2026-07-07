"""个人档案 Schema：定义档案保存入参和响应结构。"""
import datetime
from pydantic import BaseModel, Field


class ProfilePayload(BaseModel):
    gender: str | None = None
    age: int | None = Field(default=None, ge=12, le=60)
    skin_type: str | None = None
    skin_tone: str | None = None
    face_shape: str | None = None
    skin_concerns: list[str] = Field(default_factory=list)
    known_allergies: str | None = None
    period_acne: bool | None = None
    last_period_start: datetime.date | None = None
    cycle_length_days: int | None = Field(default=None, ge=20, le=45)
    pregnancy_status: str | None = None
    preference_notes: str | None = None


class ProfileResponse(ProfilePayload):
    id: int
    user_id: str
    created_at: str | None = None
    updated_at: str | None = None

    model_config = {"from_attributes": True}
