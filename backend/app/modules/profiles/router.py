"""个人档案路由：提供当前用户护肤档案读写接口。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.deps import get_db
from backend.app.modules.profiles.schemas import ProfilePayload, ProfileResponse
from backend.app.modules.profiles.service import ProfileService
from backend.app.core.schemas import StandardResponse

router = APIRouter(prefix="/profiles", tags=["个人档案"])


@router.get("/{user_id}", response_model=StandardResponse[ProfileResponse | None])
def get_profile(user_id: str, db: Session = Depends(get_db)):
    profile = ProfileService(db).get(user_id)
    return {
        "code": 200,
        "message": "success",
        "data": profile.to_dict() if profile else None
    }


@router.put("/{user_id}", response_model=StandardResponse[ProfileResponse])
def save_profile(user_id: str, data: ProfilePayload, db: Session = Depends(get_db)):
    return {
        "code": 200,
        "message": "success",
        "data": ProfileService(db).save(user_id, data).to_dict()
    }
