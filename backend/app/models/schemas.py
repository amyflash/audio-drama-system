from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ==================== Common ====================
class SuccessResponse(BaseModel):
    success: bool
    data: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: str = "Unknown error"


# ==================== Auth ====================
class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


# ==================== Album ====================
class AlbumCreate(BaseModel):
    title: str
    cover_image: str  # Base64编码的图片
    description: Optional[str] = None
    sort_order: int = 0


class AlbumUpdate(BaseModel):
    title: Optional[str] = None
    cover_image: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


class AlbumResponse(BaseModel):
    id: int
    title: str
    cover_image: str
    description: Optional[str] = None
    sort_order: int
    episode_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlbumsListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AlbumResponse]


# ==================== Episode ====================
class EpisodeCreate(BaseModel):
    title: str
    sort_order: int = 0


class EpisodeUpdate(BaseModel):
    title: Optional[str] = None
    sort_order: Optional[int] = None


class EpisodeResponse(BaseModel):
    id: int
    album_id: int
    title: str
    duration: int
    sort_order: int
    created_at: datetime
    stream_url: Optional[str] = None

    class Config:
        from_attributes = True


class EpisodesListResponse(BaseModel):
    album_id: int
    items: list[EpisodeResponse]


# ==================== Upload ====================
class UploadResponse(BaseModel):
    success: bool
    count: int
    episodes: list[EpisodeResponse]


# ==================== Stream ====================
class StreamTokenRequest(BaseModel):
    episode_id: int
