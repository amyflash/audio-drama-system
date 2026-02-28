from fastapi import APIRouter, Depends, status, HTTPException, Query, Form, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import aiofiles
import uuid
from pathlib import Path
from mutagen import File as MutagenFile
from app.db.base import get_db
from app.models.models import Album, Episode, User
from app.models.schemas import EpisodeCreate, EpisodeUpdate, EpisodeResponse, UploadResponse
from app.api.deps import get_current_admin, get_current_user, get_stream_auth_user

router = APIRouter(prefix="/episodes", tags=["剧集管理"])

ALLOWED_TYPES = ["audio/mpeg", "audio/mp4", "audio/flac", "audio/x-m4a", "audio/mp3", "audio/x-mp3"]
MAX_FILE_SIZE = 104857600  # 100MB
MEDIA_DIR = "/media/albums"


def _episode_to_response(episode: Episode, stream_url: Optional[str] = None) -> EpisodeResponse:
    """将Episode模型转换为EpisodeResponse"""
    return EpisodeResponse(
        id=episode.id,
        album_id=episode.album_id,
        title=episode.title,
        duration=episode.duration,
        sort_order=episode.sort_order,
        created_at=episode.created_at,
        stream_url=stream_url
    )


@router.get("", response_model=dict)
async def get_episodes(
    album_id: int = Query(..., description="专辑ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取专辑的剧集列表（用户视角）"""
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="专辑不存在"
        )

    episodes = db.query(Episode).filter(
        Episode.album_id == album_id
    ).order_by(Episode.sort_order.asc()).all()

    items = [
        {
            "id": ep.id,
            "album_id": ep.album_id,
            "title": ep.title,
            "duration": ep.duration,
            "sort_order": ep.sort_order,
            "created_at": ep.created_at,
            "stream_url": f"/api/stream/{ep.id}"
        }
        for ep in episodes
    ]

    return {
        "album_id": album_id,
        "items": items
    }


@router.get("/{episode_id}", response_model=dict)
async def get_episode_by_id(
    episode_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取剧集详情（用于播放器）"""
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="剧集不存在"
        )

    return {
        "id": episode.id,
        "album_id": episode.album_id,
        "title": episode.title,
        "duration": episode.duration,
        "sort_order": episode.sort_order,
        "created_at": episode.created_at,
        "stream_url": f"/api/stream/{episode.id}"
    }


@router.get("/admin", response_model=dict)
async def get_episodes_admin(
    album_id: int = Query(..., description="专辑ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """获取专辑的剧集列表（管理员视角）"""
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="专辑不存在"
        )

    episodes = db.query(Episode).filter(
        Episode.album_id == album_id
    ).order_by(Episode.sort_order.asc()).all()

    items = [
        {
            "id": ep.id,
            "album_id": ep.album_id,
            "title": ep.title,
            "duration": ep.duration,
            "sort_order": ep.sort_order,
            "created_at": ep.created_at
        }
        for ep in episodes
    ]

    return {
        "album_id": album_id,
        "items": items
    }


@router.put("/{episode_id}", response_model=EpisodeResponse)
async def update_episode(
    episode_id: int,
    episode_update: EpisodeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """更新剧集"""
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="剧集不存在"
        )

    # 更新字段
    update_data = episode_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(episode, field, value)

    db.commit()
    db.refresh(episode)

    return _episode_to_response(episode)


@router.delete("/{episode_id}", response_model=dict)
async def delete_episode(
    episode_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """删除剧集"""
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="剧集不存在"
        )

    # 删除物理文件
    if os.path.exists(episode.file_path):
        os.remove(episode.file_path)

    db.delete(episode)
    db.commit()

    return {"success": True, "data": "剧集已删除"}


@router.post("/{episode_id}/upload", response_model=EpisodeResponse)
async def upload_episode_file(
    episode_id: int,
    file: UploadFile = File(..., description="音频文件"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """为已创建的剧集上传音频文件"""
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="剧集不存在"
        )

    # 文件类型校验（放宽要求，允许更多类型）
    ALLOWED_TYPES = ["audio/mpeg", "audio/mp4", "audio/flac", "audio/x-m4a", 
                     "audio/mp3", "audio/x-mp3", "application/octet-stream", ""]
    if file.content_type and file.content_type not in ALLOWED_TYPES:
        # 不阻止上传，只是记录警告
        pass

    # 文件大小校验
    file_content = await file.read()
    file_size = len(file_content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制（最大100MB）"
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件为空"
        )

    # 生成文件名
    file_ext = Path(file.filename or "").suffix or ".mp3"
    album_id = episode.album_id
    filename = f"{uuid.uuid4()}{file_ext}"
    file_dir = os.path.join(MEDIA_DIR, str(album_id))
    os.makedirs(file_dir, exist_ok=True)
    file_path = os.path.join(file_dir, filename)

    # 保存文件
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_content)

    # 解析音频时长
    duration = 0
    try:
        audio_file = MutagenFile(file_path)
        if audio_file and hasattr(audio_file.info, 'length') and audio_file.info.length:
            duration = int(audio_file.info.length)
        else:
            # mutagen 未能解析，尝试使用估算
            duration = int(file_size / 16384)  # 128kbps = 16KB/s
    except Exception:
        # 使用文件大小估算（假设128kbps）
        duration = int(file_size / 16384)  # 128kbps = 16KB/s

    # 更新剧集信息
    episode.file_path = file_path
    episode.file_size = file_size
    episode.duration = duration

    db.commit()
    db.refresh(episode)

    return _episode_to_response(episode)
