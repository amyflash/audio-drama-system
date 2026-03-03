from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.models import User
from app.models.schemas import LoginRequest, LoginResponse, SuccessResponse
from app.core.security import verify_password, create_access_token
from app.core.session_crud import (
    create_session,
    delete_session,
    refresh_session,
    check_can_login,
    cleanup_expired_sessions,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["鉴权"])


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """登录接口"""
    # 0. 顺手清理一次已过期的会话，避免 sessions 表无限增长
    await cleanup_expired_sessions(db)

    # 1. 验证用户名和密码
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 2. 检查账号状态
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用",
        )

    # 3. 并发控制检查
    can_login = await check_can_login(db, user.id)
    if not can_login:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="系统在线人数已达上限，请稍后重试",
        )

    # 4. 生成Token
    access_token = create_access_token(
        data={"user_id": user.id, "role": user.role}
    )

    # 5. 创建Session
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "")
    await create_session(db, user.id, access_token, ip_address, user_agent)

    # 6. 更新最后登录时间
    from datetime import datetime

    user.last_login_at = datetime.utcnow()
    db.commit()

    from app.core.config import settings

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_SECONDS,
        user=user,
    )


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """登出接口"""
    await delete_session(db, current_user.id)
    return SuccessResponse(success=True, data="已成功登出")


@router.post("/heartbeat", response_model=SuccessResponse)
async def heartbeat(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """心跳保活接口"""
    # 定期请求心跳时也顺带清理一次
    await cleanup_expired_sessions(db)
    await refresh_session(db, current_user.id)
    from app.core.config import settings

    return SuccessResponse(
        success=True,
        data=f"心跳成功，Session将在{settings.SESSION_EXPIRE_SECONDS}秒后过期",
    )

