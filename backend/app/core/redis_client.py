import json
import redis
from app.core.config import settings

# Redis客户端
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)


async def get_current_online_count() -> int:
    """获取当前在线人数"""
    keys = redis_client.keys("session:*")
    return len(keys)


async def create_session(user_id: int, token: str, ip: str = None, user_agent: str = None) -> bool:
    """创建Session"""
    import time
    session_data = {
        "token": token,
        "user_id": user_id,
        "ip": ip or "",
        "user_agent": user_agent or "",
        "expires_at": int(time.time()) + settings.SESSION_EXPIRE_SECONDS
    }
    redis_client.setex(
        f"session:{user_id}",
        settings.SESSION_EXPIRE_SECONDS,
        json.dumps(session_data)
    )
    return True


async def delete_session(user_id: int) -> bool:
    """删除Session"""
    redis_client.delete(f"session:{user_id}")
    return True


async def refresh_session(user_id: int) -> bool:
    """刷新Session过期时间"""
    redis_client.expire(f"session:{user_id}", settings.SESSION_EXPIRE_SECONDS)
    return True


async def check_can_login(user_id: int) -> bool:
    """检查是否可以登录（并发控制）"""
    current_count = await get_current_online_count()

    # 检查当前在线数是否已达上限
    if current_count >= settings.MAX_CONCURRENT_USERS:
        # 检查用户是否已在在线列表中（允许重复登录）
        existing = redis_client.exists(f"session:{user_id}")
        if not existing:
            return False

    return True


async def get_session(user_id: int) -> dict or None:
    """获取Session"""
    data = redis_client.get(f"session:{user_id}")
    if data:
        return json.loads(data)
    return None
