from fastapi import APIRouter, Depends, status, HTTPException, Request, Query
from sqlalchemy.orm import Session
import os
from app.db.base import get_db
from app.models.models import Episode, User
from app.api.deps import get_stream_auth_user, get_current_user
from app.core.security import generate_stream_token, verify_stream_token

router = APIRouter(prefix="/stream", tags=["音频流"])


@router.get("/token/{episode_id}")
async def get_stream_token(
    episode_id: int,
    current_user: User = Depends(get_current_user)
):
    """获取音频流Token（用于播放器加载）"""
    token = generate_stream_token(current_user.id, episode_id)

    return {
        "success": True,
        "token": token,
        "expires_in": 600  # 10分钟
    }


@router.get("/{episode_id}")
async def stream_audio(
    episode_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    获取音频流（防下载核心接口）

    认证方式：
    1. Authorization header: Bearer {token}
    2. Query param: token=xxx
    3. Query param需要与episode_id匹配
    """
    # 1. 获取认证信息
    auth_token = request.headers.get("authorization", "").replace("Bearer ", "")
    query_token = request.query_params.get("token", "")

    user_id = None

    # 2. 验证Token
    if auth_token:
        # 方式1: Authorization header
        from app.core.security import decode_token
        payload = decode_token(auth_token)
        if payload and "user_id" in payload:
            user_id = payload["user_id"]
    elif query_token:
        # 方式2: 流式专用token（需要验证）
        from app.core.security import decode_token
        payload = decode_token(query_token)
        if payload and payload.get("type") == "stream":
            # 流式token需要验证user_id和episode_id匹配
            if (payload.get("user_id") and
                payload.get("episode_id") == episode_id):
                user_id = payload["user_id"]

    # 3. 检查认证是否成功
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证"
        )

    # 4. 查询音频文件
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="音频不存在"
        )

    # 5. 检查文件是否存在
    if not os.path.exists(episode.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="音频文件丢失"
        )

    # 6. 读取文件
    file_size = os.path.getsize(episode.file_path)

    # 7. 处理Range请求（断点续传）
    range_header = request.headers.get("range")
    if range_header:
        # 解析Range header（格式: bytes=start-end）
        start, end = range_header.replace("bytes=", "").split("-")
        start = int(start)
        end = int(end) if end else file_size - 1
        content_length = end - start + 1

        # 读取指定范围的数据
        with open(episode.file_path, "rb") as f:
            f.seek(start)
            data = f.read(content_length)

        # 返回206 Partial Content
        from fastapi.responses import Response
        return Response(
            content=data,
            status_code=206,
            media_type="audio/mpeg",
            headers={
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Content-Length": str(content_length),
                "Accept-Ranges": "bytes",
                "Content-Disposition": "inline",  # 强制浏览器播放
                "X-Content-Type-Options": "nosniff",
                "Cache-Control": "no-cache, no-store, must-revalidate",
            }
        )
    else:
        # 完整文件返回
        from fastapi.responses import FileResponse
        return FileResponse(
            episode.file_path,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline",  # 强制浏览器播放
                "X-Content-Type-Options": "nosniff",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Accept-Ranges": "bytes",
            }
        )
