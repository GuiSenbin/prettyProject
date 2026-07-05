"""用户模块路由：处理纯净版基础用户 CRUD。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.deps import get_db
from backend.app.modules.users.schemas import UserCreate, UserResponse
from backend.app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/latest", response_model=UserResponse | None)
def get_latest_user(db: Session = Depends(get_db)):
    user = UserService(db).latest()
    return user.to_dict() if user else None


@router.post("/", response_model=UserResponse)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    return UserService(db).create(data.model_dump()).to_dict()


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserCreate, db: Session = Depends(get_db)):
    return UserService(db).update(user_id, data.model_dump()).to_dict()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return UserService(db).get_or_404(user_id).to_dict()


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    UserService(db).delete(user_id)
    return {"ok": True}
