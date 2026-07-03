"""用户资料 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.deps import get_db
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/latest", response_model=UserResponse | None)
def get_latest_user(db: Session = Depends(get_db)):
    """获取最新的用户（兼容旧版单人演示入口）"""
    user = db.execute(
        select(User).order_by(User.id.desc()).limit(1)
    ).scalar_one_or_none()
    return user.to_dict() if user else None


@router.post("/", response_model=UserResponse)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    """创建游客/新用户档案"""
    user = User(**data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.to_dict()


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserCreate, db: Session = Depends(get_db)):
    """更新当前用户档案"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "用户不存在")

    for key, val in data.model_dump().items():
        setattr(user, key, val)
    db.commit()
    db.refresh(user)
    return user.to_dict()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "用户不存在")
    return user.to_dict()


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "用户不存在")
    db.delete(user)
    db.commit()
    return {"ok": True}
