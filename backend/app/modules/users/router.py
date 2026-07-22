"""用户模块路由：处理企业级账号注册、登录与 CRUD。"""
import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.deps import get_current_user_id, get_db
from backend.app.modules.users.schemas import UserCreate, UserResponse, UserRegister, UserLogin, UserUpdate
from backend.app.modules.users.service import UserService
from backend.app.core.schemas import StandardResponse

router = APIRouter(prefix="/users", tags=["用户"])


@router.post("/register", response_model=StandardResponse[UserResponse])
def register(data: UserRegister, db: Session = Depends(get_db)):
    """账号密码注册"""
    user = UserService(db).register_user(data.username, data.password, data.display_name)
    return {
        "code": 200,
        "message": "success",
        "data": user.to_dict()
    }


@router.post("/login", response_model=StandardResponse[UserResponse])
def login(data: UserLogin, db: Session = Depends(get_db)):
    """账号密码登录（支持用户名/手机号）"""
    user = UserService(db).authenticate_user(data.username, data.password)
    return {
        "code": 200,
        "message": "success",
        "data": user.to_dict()
    }


@router.get("/latest", response_model=StandardResponse[UserResponse | None])
def get_latest_user(db: Session = Depends(get_db)):
    user = UserService(db).latest()
    return {
        "code": 200,
        "message": "success",
        "data": user.to_dict() if user else None
    }


@router.post("/", response_model=StandardResponse[UserResponse])
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    return {
        "code": 200,
        "message": "success",
        "data": UserService(db).create(data.model_dump()).to_dict()
    }


@router.get("/me", response_model=StandardResponse[UserResponse])
def get_current_user(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return {
        "code": 200,
        "message": "success",
        "data": UserService(db).get_or_404(user_id).to_dict()
    }


@router.put("/me", response_model=StandardResponse[UserResponse])
def update_current_user(
    data: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return {
        "code": 200,
        "message": "success",
        "data": UserService(db).update(user_id, data.model_dump(exclude_unset=True)).to_dict()
    }


@router.post("/me/avatar", response_model=StandardResponse[UserResponse])
async def upload_current_user_avatar(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return await _upload_avatar_for_user(user_id, file, db)


@router.delete("/me", response_model=StandardResponse[dict])
def delete_current_user(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    UserService(db).delete(user_id)
    return {
        "code": 200,
        "message": "success",
        "data": {"ok": True}
    }


@router.put("/{user_id}", response_model=StandardResponse[UserResponse])
def update_user(user_id: str, data: UserUpdate, db: Session = Depends(get_db)):
    return {
        "code": 200,
        "message": "success",
        "data": UserService(db).update(user_id, data.model_dump(exclude_unset=True)).to_dict()
    }


@router.get("/{user_id}", response_model=StandardResponse[UserResponse])
def get_user(user_id: str, db: Session = Depends(get_db)):
    return {
        "code": 200,
        "message": "success",
        "data": UserService(db).get_or_404(user_id).to_dict()
    }


@router.post("/{user_id}/avatar", response_model=StandardResponse[UserResponse])
async def upload_avatar(user_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await _upload_avatar_for_user(user_id, file, db)


async def _upload_avatar_for_user(user_id: str, file: UploadFile, db: Session):
    service = UserService(db)
    service.get_or_404(user_id)
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="未上传文件")
    
    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    filename = f"{uuid.uuid4().hex}.{ext}"
    dirpath = "backend/static/avatars"
    os.makedirs(dirpath, exist_ok=True)
    filepath = os.path.join(dirpath, filename)
    
    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)
        
    avatar_url = f"/static/avatars/{filename}"
    updated_user = service.update(user_id, {"avatar_url": avatar_url})
    return {
        "code": 200,
        "message": "success",
        "data": updated_user.to_dict()
    }


@router.delete("/{user_id}", response_model=StandardResponse[dict])
def delete_user(user_id: str, db: Session = Depends(get_db)):
    UserService(db).delete(user_id)
    return {
        "code": 200,
        "message": "success",
        "data": {"ok": True}
    }
