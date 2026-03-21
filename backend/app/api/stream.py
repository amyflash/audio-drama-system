"""
音频流路由
支持两种认证方式：
  1. SSO token（Authorization: Bearer <sso_token>），payload 里 user_id 在 sub 字段
  2. Stream 专用 token（?token=<stream_token>），payload 里有 type=stream / user_id / episode_id
"""
from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import Response, FileResponse
from sqlalchemy.orm import Session
import sys
from datetime import datetime, timedelta
from pathlib import Path
from jose import JWTError, jwt

from app.db.base import get_db
from app.models.models import Episode
from app.api.sso import get_current_user_from_token
from app.core.config import settings

router = APIRouter(prefix="/stream", tags=["音频流"])


# ---------------------------------------------------------------------------
# Token 工具
# ---------------------------------------------------------------------------

def generate_stream_token(user_id: int, episode_id: int) -> str:
    """生成音频流专用短期 JWT"""
    payload = {
        "type": "stream",
        "user_id": user_id,
        "episode_id": episode_id,
        "exp": datetime.utcnow() + timedelta(seconds=settings.STREAM_TOKEN_EXPIRE_SECONDS),
    }
    return jwt.encode(payload, settings.SSO_SECRET_KEY, algorithm=settings.SSO_ALGORITHM)


def decode_sso_token(token: str):
    """
    解码 SSO token（jwt-auth 签发），提取 user_id。
    SSO token 的 user_id 在 'sub' 字段。
    返回 int 或 None。
    """
    try:
        payload = jwt.decode(token, settings.SSO_SECRET_KEY, algorithms=[settings.SSO_ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            return None
        return int(sub)
    except (JWTError, ValueError):
        return None


def decode_stream_token(token: str, episode_id: int):
    """
    解码 stream 专用 token，校验 type / episode_id，提取 user_id。
    Stream token 的 user_id 在 'user_id' 字段。
    返回 int 或 None。
    """
    try:
        payload = jwt.decode(token, settings.SSO_SECRET_KEY, algorithms=[settings.SSO_ALGORITHM])
        if payload.get("type") != "stream":
            return None
        if payload.get("episode_id") != episode_id:
            return None
        user_id = payload.get("user_id")
        if user_id is None:
            return None
        return int(user_id)
    except (JWTError, ValueError):
        return None


# ---------------------------------------------------------------------------
# 路径工具
# ---------------------------------------------------------------------------

def resolve_file_path(file_path: str) -> Path:
    """
    将数据库存储的路径解析为当前系统绝对路径。
    - 绝对路径直接使用
    - 相对路径以 MEDIA_DIR 为基准
    - Windows 自动加长路径前缀
    """
    p = Path(file_path)

    if p.is_absolute():
        resolved = p.resolve()
    else:
        media_dir = Path(settings.MEDIA_DIR)
        if not media_dir.is_absolute():
            media_dir = Path(__file__).resolve().parent.parent.parent / media_dir
        resolved = (media_dir / p).resolve()

    if sys.platform == "win32":
        resolved = Path("\\\\?\\" + str(resolved))

    return resolved


# ---------------------------------------------------------------------------
# 路由
# ---------------------------------------------------------------------------

@router.get("/token/{episode_id}")
async def get_stream_token(episode_id: int, request: Request):
    """
    获取音频流专用 Token。
    未登录直接返回 401，前端应引导用户登录。
    """
    user = get_current_user_from_token(request)  # 失败自动抛 401
    token = generate_stream_token(user.id, episode_id)
    return {
        "success": True,
        "token": token,
        "expires_in": settings.STREAM_TOKEN_EXPIRE_SECONDS,
    }


@router.get("/{episode_id}")
async def stream_audio(
    episode_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    音频流接口（防下载）。

    认证优先级：
    1. ?token=xxx              -> stream 专用 token（播放器直接嵌 URL 时使用）
    2. Authorization: Bearer   -> SSO token（Ajax 请求时使用）
    """
    user_id = None

    # 方式 1：stream 专用 token（query param）
    query_token = request.query_params.get("token", "")
    if query_token:
        user_id = decode_stream_token(query_token, episode_id)

    # 方式 2：SSO token（Authorization header）
    if user_id is None:
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            user_id = decode_sso_token(auth_header[7:])

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 查询剧集
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="音频不存在")

    # 解析文件路径
    file_path = resolve_file_path(episode.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"音频文件丢失: {episode.file_path}",
        )

    file_size = file_path.stat().st_size
    file_path_str = str(file_path)

    base_headers = {
        "Content-Disposition": "inline",
        "X-Content-Type-Options": "nosniff",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Accept-Ranges": "bytes",
    }

    # Range 请求（断点续传）
    range_header = request.headers.get("range")
    if range_header:
        try:
            range_val = range_header.replace("bytes=", "")
            start_str, end_str = range_val.split("-", 1)
            start = int(start_str)
            end = int(end_str) if end_str else file_size - 1
        except ValueError:
            raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

        if start > end or end >= file_size:
            raise HTTPException(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                headers={"Content-Range": f"bytes */{file_size}"},
            )

        content_length = end - start + 1
        with open(file_path_str, "rb") as f:
            f.seek(start)
            data = f.read(content_length)

        return Response(
            content=data,
            status_code=206,
            media_type="audio/mpeg",
            headers={
                **base_headers,
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Content-Length": str(content_length),
            },
        )

    # 完整文件
    return FileResponse(file_path_str, media_type="audio/mpeg", headers=base_headers)
