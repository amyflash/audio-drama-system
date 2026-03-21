"""
SSO 单点登录模块
用于验证来自 jwt-auth 的 token
"""
from typing import Optional
from jose import JWTError, jwt

from app.core.config import settings


def decode_external_token(token: str) -> Optional[dict]:
    """
    使用 jwt-auth 的密钥解码 token

    Args:
        token: jwt-auth 签发的 JWT token

    Returns:
        解码后的 payload，失败返回 None
    """
    try:
        payload = jwt.decode(
            token,
            settings.SSO_SECRET_KEY,
            algorithms=[settings.SSO_ALGORITHM]
        )
        # 验证必要字段
        if payload.get("sub") is None:
            return None
        return payload
    except JWTError:
        return None
