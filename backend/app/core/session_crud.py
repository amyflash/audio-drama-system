from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from app.models.models import Session as SessionModel
from app.core.config import settings


def get_db_session():
    """获取数据库会话的依赖"""
    from app.db.base import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def cleanup_expired_sessions(db: Session) -> int:
    """
    清理已过期的会话记录

    返回删除的记录数量，用于日志或调试（生产环境可忽略返回值）。
    """
    now = datetime.utcnow()
    deleted = db.query(SessionModel).filter(
        SessionModel.expires_at <= now
    ).delete()
    db.commit()
    return deleted


async def get_current_online_count(db: Session) -> int:
    """获取当前在线人数"""
    now = datetime.utcnow()
    count = db.query(SessionModel).filter(
        SessionModel.expires_at > now
    ).count()
    return count


async def create_session(db: Session, user_id: int, token: str, ip: str = None, user_agent: str = None) -> bool:
    """创建Session"""
    expires_at = datetime.utcnow() + timedelta(seconds=settings.SESSION_EXPIRE_SECONDS)

    session = SessionModel(
        user_id=user_id,
        token=token,
        ip_address=ip or "",
        user_agent=user_agent or "",
        expires_at=expires_at
    )
    db.add(session)
    db.commit()
    return True


async def delete_session(db: Session, user_id: int) -> bool:
    """删除Session（根据 user_id）"""
    db.query(SessionModel).filter(
        SessionModel.user_id == user_id
    ).delete()
    db.commit()
    return True


async def delete_session_by_token(db: Session, token: str) -> bool:
    """删除Session（根据 token）"""
    db.query(SessionModel).filter(
        SessionModel.token == token
    ).delete()
    db.commit()
    return True


async def refresh_session(db: Session, user_id: int) -> bool:
    """刷新Session过期时间"""
    expires_at = datetime.utcnow() + timedelta(seconds=settings.SESSION_EXPIRE_SECONDS)
    db.query(SessionModel).filter(
        SessionModel.user_id == user_id
    ).update({"expires_at": expires_at})
    db.commit()
    return True


async def check_can_login(db: Session, user_id: int) -> bool:
    """检查是否可以登录（并发控制）"""
    # 去掉并发控制，始终允许登录
    return True


async def get_session(db: Session, user_id: int) -> dict | None:
    """获取Session"""
    now = datetime.utcnow()
    session = db.query(SessionModel).filter(
        and_(
            SessionModel.user_id == user_id,
            SessionModel.expires_at > now
        )
    ).first()

    if session:
        return {
            "token": session.token,
            "user_id": session.user_id,
            "ip": session.ip_address,
            "user_agent": session.user_agent,
            "expires_at": int(session.expires_at.timestamp())
        }
    return None
