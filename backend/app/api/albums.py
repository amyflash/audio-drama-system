from fastapi import APIRouter, Depends, status, HTTPException, Query, Form, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import aiofiles
import uuid
from pathlib import Path
from mutagen import File as MutagenFile
from app.db.base import get_db
from app.models.models import Album, Episode, User
from app.models.schemas import (
    AlbumCreate, AlbumUpdate, AlbumResponse,
    AlbumsListResponse, EpisodeCreate, EpisodeResponse, EpisodeUpdate
)
from app.api.deps import get_current_admin, get_current_user
from app.core.config import settings

router = APIRouter(prefix="/albums", tags=["专辑管理"])


def _album_to_response(album: Album) -> AlbumResponse:
    """将Album模型转换为AlbumResponse"""
    return AlbumResponse(
        id=album.id,
        title=album.title,
        cover_image=album.cover_image,
        description=album.description,
        sort_order=album.sort_order,
        episode_count=album.episode_count,
        created_at=album.created_at,
        updated_at=album.updated_at
    )


@router.get("", response_model=AlbumsListResponse)
async def get_albums(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取专辑列表（分页）"""
    # 计算总数
    total = db.query(Album).count()

    # 查询专辑（分页）
    albums = db.query(Album).order_by(
        Album.sort_order.asc(),
        Album.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    items = [_album_to_response(album) for album in albums]

    return AlbumsListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.post("", response_model=AlbumResponse, status_code=status.HTTP_201_CREATED)
async def create_album(
    album_data: AlbumCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """创建专辑"""
    album = Album(
        title=album_data.title,
        cover_image=album_data.cover_image,
        description=album_data.description,
        sort_order=album_data.sort_order
    )
    db.add(album)
    db.commit()
    db.refresh(album)

    return _album_to_response(album)


@router.get("/{album_id}", response_model=AlbumResponse)
async def get_album(
    album_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取专辑详情"""
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="专辑不存在"
        )

    return _album_to_response(album)


@router.put("/{album_id}", response_model=AlbumResponse)
async def update_album(
    album_id: int,
    album_update: AlbumUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """更新专辑"""
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="专辑不存在"
        )

    # 更新字段
    update_data = album_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(album, field, value)

    db.commit()
    db.refresh(album)

    return _album_to_response(album)


@router.delete("/{album_id}", response_model=dict)
async def delete_album(
    album_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """删除专辑（级联删除所有剧集）"""
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="专辑不存在"
        )

    # 删除专辑及关联的剧集（级联删除）
    db.delete(album)
    db.commit()

    return {"success": True, "data": "专辑已删除"}


# ==================== 专辑的剧集管理 ====================

ALLOWED_TYPES = ["audio/mpeg", "audio/mp4", "audio/flac", "audio/x-m4a", "audio/mp3", "audio/x-mp3"]
MAX_FILE_SIZE = 104857600  # 100MB
MEDIA_DIR = "/media/albums"


@router.get("/{album_id}/episodes", response_model=dict)
async def get_album_episodes(
    album_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取专辑的剧集列表"""
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


@router.post("/{album_id}/episodes", response_model=EpisodeResponse, status_code=status.HTTP_201_CREATED)
async def create_episode(
    album_id: int,
    episode_data: EpisodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """创建剧集（不含音频文件）"""
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="专辑不存在"
        )

    episode = Episode(
        album_id=album_id,
        title=episode_data.title,
        duration=0,
        sort_order=episode_data.sort_order or album.episode_count + 1
    )
    db.add(episode)
    db.commit()
    db.refresh(episode)

    return EpisodeResponse(
        id=episode.id,
        album_id=episode.album_id,
        title=episode.title,
        duration=episode.duration,
        sort_order=episode.sort_order,
        created_at=episode.created_at
    )


@router.post("/{album_id}/episodes/batch-upload", response_model=dict)
async def batch_upload_episodes(
    album_id: int,
    files: list[UploadFile] = File(..., description="音频文件列表"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """批量上传音频文件到专辑"""
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="专辑不存在"
        )

    uploaded_episodes = []

    for upload_file in files:
        print(f"Processing file: {upload_file.filename}, content_type: {upload_file.content_type}")

        # 文件类型校验（更宽松，允许空类型）
        if upload_file.content_type and upload_file.content_type not in ALLOWED_TYPES and upload_file.content_type != "application/octet-stream":
            print(f"Skipping file due to unsupported content_type: {upload_file.content_type}")
            continue  # 跳过不支持的文件类型

        # 文件大小校验
        file_content = await upload_file.read()
        file_size = len(file_content)
        print(f"File size: {file_size} bytes")

        if file_size > MAX_FILE_SIZE or file_size == 0:
            print(f"Skipping file due to size issue: 0 < {file_size} < {MAX_FILE_SIZE}")
            continue

        # 生成文件名
        file_ext = Path(upload_file.filename or "").suffix or ".mp3"
        filename = f"{uuid.uuid4()}{file_ext}"
        file_dir = os.path.join(MEDIA_DIR, str(album_id))
        os.makedirs(file_dir, exist_ok=True)
        file_path = os.path.join(file_dir, filename)

        # 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)

        print(f"File saved to: {file_path}")

        # 解析音频时长
        duration = 0
        try:
            audio_file = MutagenFile(file_path)
            if audio_file and hasattr(audio_file.info, 'length') and audio_file.info.length:
                duration = int(audio_file.info.length)
                print(f"Audio duration parsed: {duration} seconds")
            else:
                # mutagen 未能解析，尝试使用估算
                print("Mutagen failed to parse duration, using file size estimation")
                duration = int(file_size / 16384)  # 128kbps = 16KB/s
                print(f"Estimated duration from file size: {duration} seconds")
        except Exception as e:
            print(f"Failed to parse audio metadata: {e}")
            # 使用文件大小估算（假设128kbps）
            duration = int(file_size / 16384)  # 128kbps = 16KB/s
            print(f"Estimated duration from file size: {duration} seconds")

        # 创建剧集记录
        episode = Episode(
            album_id=album_id,
            title=Path(upload_file.filename or f"音频{len(uploaded_episodes)+1}").stem,
            file_path=file_path,
            file_size=file_size,
            duration=duration,
            sort_order=album.episode_count + 1
        )
        db.add(episode)

        # 更新专辑的episode_count
        album.episode_count += 1

        uploaded_episodes.append(episode)
        print(f"Episode created successfully")

    # 提交事务
    db.commit()
    print(f"Transaction committed, uploaded {len(uploaded_episodes)} episodes")

    # 刷新所有episode以获取ID
    for ep in uploaded_episodes:
        db.refresh(ep)

    return {
        "success": True,
        "uploaded": len(uploaded_episodes),
        "total": len(files)
    }
