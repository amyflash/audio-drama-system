from fastapi import APIRouter, Depends, status, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
import os
import aiofiles
from mutagen import File as MutagenFile
from app.db.base import get_db
from app.models.models import Album, Episode, User
from app.models.schemas import UploadResponse
from app.api.deps import get_current_admin, get_current_user
import uuid
from pathlib import Path

router = APIRouter(prefix="/upload", tags=["文件上传"])

# 允许的文件类型
ALLOWED_TYPES = ["audio/mpeg", "audio/mp4", "audio/flac", "audio/x-m4a", "audio/mp3"]

# 最大文件大小（100MB）
MAX_FILE_SIZE = 104857600


@router.post("/batch", response_model=UploadResponse)
async def batch_upload(
    album_id: int = Form(..., description="专辑ID"),
    files: list[UploadFile] = File(..., description="音频文件列表"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """批量上传音频文件到指定专辑"""

    # 验证专辑是否存在
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="专辑不存在"
        )

    uploaded_episodes = []
    media_dir = "/media/albums"

    for upload_file in files:
        # 1. 文件类型校验
        if upload_file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型: {upload_file.content_type}（仅支持MP3、M4A、FLAC）"
            )

        # 2. 文件大小校验
        file_content = await upload_file.read()
        file_size = len(file_content)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小超过限制（最大100MB）: {upload_file.filename}"
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件为空"
            )

        # 3. 生成文件名（UUID + 原始扩展名）
        file_ext = Path(upload_file.filename).suffix
        filename = f"{uuid.uuid4()}{file_ext}"
        file_dir = os.path.join(media_dir, str(album_id))
        os.makedirs(file_dir, exist_ok=True)
        file_path = os.path.join(file_dir, filename)

        # 4. 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)

        # 5. 解析音频元数据（时长）
        duration = 0
        try:
            audio_file = MutagenFile(file_path)
            if audio_file and hasattr(audio_file.info, 'length') and audio_file.info.length:
                duration = int(audio_file.info.length)
            else:
                # mutagen 未能解析，尝试使用估算
                duration = int(file_size / 16384)  # 128kbps = 16KB/s
        except Exception as e:
            # 解析失败，使用文件大小估算
            duration = int(file_size / 16384)  # 128kbps = 16KB/s

        # 6. 创建剧集记录
        episode = Episode(
            album_id=album_id,
            title=upload_file.filename.rsplit(file_ext, 1)[0],  # 去除扩展名作为标题
            file_path=file_path,
            file_size=file_size,
            duration=duration,
            sort_order=album.episode_count + 1  # 自动递增排序
        )
        db.add(episode)

        # 7. 更新专辑的episode_count
        album.episode_count += 1

        uploaded_episodes.append(episode)

    # 8. 提交事务
    db.commit()

    # 9. 刷新所有episode以获取ID
    for ep in uploaded_episodes:
        db.refresh(ep)

    # 10. 返回结果
    episodes_response = [
        {
            "id": ep.id,
            "album_id": ep.album_id,
            "title": ep.title,
            "duration": ep.duration,
            "sort_order": ep.sort_order,
            "created_at": ep.created_at
        }
        for ep in uploaded_episodes
    ]

    return UploadResponse(
        success=True,
        count=len(uploaded_episodes),
        episodes=episodes_response
    )


@router.post("/cover", response_model=dict)
async def upload_cover(
    image: UploadFile = File(..., description="封面图片"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """上传专辑封面图片（Base64编码）"""

    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能上传图片文件"
        )

    # 读取文件
    import base64
    file_content = await image.read()
    base64_data = base64.b64encode(file_content).decode('utf-8')

    # 返回Base64编码的图片
    return {
        "success": True,
        "data": base64_data,
        "format": image.content_type
    }
