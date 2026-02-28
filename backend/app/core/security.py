from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """加密密码"""
    # bcrypt max 72 bytes
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def create_access_token(data: dict) -> str:
    """创建JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRE_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """解码JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def generate_stream_token(user_id: int, episode_id: int) -> str:
    """生成音频流Token"""
    data = {
        "user_id": user_id,
        "episode_id": episode_id,
        "type": "stream",
        "exp": datetime.utcnow() + timedelta(seconds=settings.STREAM_TOKEN_EXPIRE_SECONDS)
    }
    return jwt.encode(
        data,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def verify_stream_token(token: str, user_id: int, episode_id: int) -> bool:
    """验证音频流Token"""
    payload = decode_token(token)
    if not payload:
        return False
    return (
        payload.get("user_id") == user_id and
        payload.get("episode_id") == episode_id and
        payload.get("type") == "stream"
    )
