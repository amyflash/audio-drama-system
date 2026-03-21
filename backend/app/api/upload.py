from fastapi import APIRouter, Depends, status, HTTPException, Form, UploadFile, File, Request
from sqlalchemy.orm import Session
import os
import sys
import aiofiles
from mutagen import File as MutagenFile
from app.db.base import get_db
from app.models.models import Album, Episode
from app.models.schemas import UploadResponse
from app.api.sso import require_admin
import uuid
from pathlib import Path
from app.core.config import settings

router = APIRouter(prefix="/upload", tags=["文件上传"])

# 允许的文件类型
ALLOWED_TYPES = ["audio/mpeg", "audio/mp4", "audio/flac", "audio/x-m4a", "audio/mp3"]

# 最大文件大小（100MB）
MAX_FILE_SIZE = settings.UPLOAD_MAX_FILE_SIZE


def resolve_media_dir() -> Path:
    """
    解析媒体目录的绝对路径，兼容 Windows 和 Linux。

    - 优先使用配置中的绝对路径
    - 若为相对路径，则以项目根目录（本文件上三级）为基准解析
    - Windows 上自动添加长路径前缀（\\\\?\\）以突破 260 字符限制
    """
    configured = settings.MEDIA_DIR
    path = Path(configured)

    if not path.is_absolute():
        # 以项目根目录为基准（upload.py → api → app → project_root）
        project_root = Path(__file__).resolve().parent.parent.parent
        path = project_root / path

    path = path.resolve()

    # Windows 长路径支持：添加 \\?\ 前缀
    if sys.platform == "win32":
        path = Path("\\\\?\\" + str(path))

    return path


def make_file_path(media_dir: Path, album_id: int, filename: str) -> Path:
    """
    构造音频文件的存储路径，并确保目录存在。
    返回 Path 对象（Windows 已含长路径前缀）。
    """
    file_dir = media_dir / str(album_id)
    file_dir.mkdir(parents=True, exist_ok=True)
    return file_dir / filename


def path_to_str(path: Path) -> str:
    """
    将 Path 对象转为字符串，统一使用正斜杠（便于跨平台存储到数据库）。
    Windows 长路径前缀（\\\\?\\）会在此处去除，只保留正常路径字符串。
    """
    path_str = str(path)
    # 去除 Windows 长路径前缀后再统一斜杠
    if path_str.startswith("\\\\?\\"):
        path_str = path_str[4:]
    return path_str.replace("\\", "/")


def get_audio_duration(file_path: Path, file_size: int) -> int:
    """
    解析音频时长（秒）。
    解析失败时按 128kbps 估算，避免因 Windows 文件锁或格式问题导致崩溃。
    """
    try:
        audio_file = MutagenFile(str(file_path))
        if audio_file and hasattr(audio_file, "info") and hasattr(audio_file.info, "length"):
            length = audio_file.info.length
            if length:
                return int(length)
    except Exception:
        pass

    # 回退：按 128kbps = 16 KB/s 估算
    return max(1, int(file_size / 16384))


@router.post("/batch", response_model=UploadResponse)
async def batch_upload(
    request: Request,
    album_id: int = Form(..., description="专辑ID"),
    files: list[UploadFile] = File(..., description="音频文件列表"),
    db: Session = Depends(get_db),
):
    """批量上传音频文件到指定专辑"""
    # 验证管理员权限
    require_admin(request)

    # 验证专辑是否存在
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="专辑不存在"
        )

    media_dir = resolve_media_dir()
    uploaded_episodes = []

    for upload_file in files:
        # 1. 文件类型校验
        if upload_file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型: {upload_file.content_type}（仅支持MP3、M4A、FLAC）"
            )

        # 2. 读取文件内容并校验大小
        file_content = await upload_file.read()
        file_size = len(file_content)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件为空: {upload_file.filename}"
            )

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小超过限制（最大100MB）: {upload_file.filename}"
            )

        # 3. 生成安全文件名（UUID + 原始扩展名）
        # 使用 PurePosixPath 提取扩展名，避免 Windows 路径中反斜杠干扰
        original_name = Path(upload_file.filename).name  # 只取文件名部分
        file_ext = Path(original_name).suffix.lower()    # 统一小写扩展名
        filename = f"{uuid.uuid4()}{file_ext}"

        # 4. 构造存储路径并保存文件
        file_path = make_file_path(media_dir, album_id, filename)

        async with aiofiles.open(str(file_path), "wb") as f:
            await f.write(file_content)

        # 5. 解析音频时长
        duration = get_audio_duration(file_path, file_size)

        # 6. 提取标题（去除扩展名）
        title = Path(original_name).stem

        # 7. 创建剧集记录（file_path 统一存为正斜杠字符串）
        episode = Episode(
            album_id=album_id,
            title=title,
            file_path=path_to_str(file_path),
            file_size=file_size,
            duration=duration,
            sort_order=album.episode_count + 1,
        )
        db.add(episode)
        album.episode_count += 1
        uploaded_episodes.append(episode)

    # 8. 提交事务
    db.commit()

    # 9. 刷新所有 episode 以获取数据库生成的 ID
    for ep in uploaded_episodes:
        db.refresh(ep)

    # 10. 构造响应
    episodes_response = [
        {
            "id": ep.id,
            "album_id": ep.album_id,
            "title": ep.title,
            "duration": ep.duration,
            "sort_order": ep.sort_order,
            "created_at": ep.created_at,
        }
        for ep in uploaded_episodes
    ]

    return UploadResponse(
        success=True,
        count=len(uploaded_episodes),
        episodes=episodes_response,
    )


