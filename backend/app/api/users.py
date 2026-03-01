from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.db.base import get_db
from app.models.models import User
from app.api.deps import get_current_admin
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["用户管理"])


# ==================== Schemas ====================
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    role: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    created_at: str
    last_login_at: str | None = None

    class Config:
        from_attributes = True


class UsersListResponse(BaseModel):
    total: int
    items: List[UserResponse]


# ==================== API Endpoints ====================


@router.get("", response_model=UsersListResponse)
async def get_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """获取用户列表（管理员）"""
    total = db.query(User).count()
    users = db.query(User).order_by(User.created_at.desc()).all()

    items = [
        UserResponse(
            id=user.id,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else "",
            last_login_at=user.last_login_at.isoformat() if user.last_login_at else None
        )
        for user in users
    ]

    return UsersListResponse(total=total, items=items)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """获取用户详情（管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise Exception("用户不存在")

    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else "",
        last_login_at=user.last_login_at.isoformat() if user.last_login_at else None
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """创建用户（管理员）"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise Exception("用户名已存在")

    # 创建新用户
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else "",
        last_login_at=user.last_login_at.isoformat() if user.last_login_at else None
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """更新用户（管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise Exception("用户不存在")

    # 更新字段
    if user_update.username is not None:
        # 检查新用户名是否已存在
        existing_user = db.query(User).filter(
            User.username == user_update.username,
            User.id != user_id
        ).first()
        if existing_user:
            raise Exception("用户名已存在")
        user.username = user_update.username

    if user_update.password is not None:
        user.password_hash = get_password_hash(user_update.password)

    if user_update.role is not None:
        user.role = user_update.role

    if user_update.is_active is not None:
        user.is_active = user_update.is_active

    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else "",
        last_login_at=user.last_login_at.isoformat() if user.last_login_at else None
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """删除用户（管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise Exception("用户不存在")

    # 禁止删除自己
    if user_id == current_admin.id:
        raise Exception("不能删除当前登录的管理员")

    db.delete(user)
    db.commit()

    return {"success": True, "data": "用户已删除"}
