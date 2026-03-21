from pydantic_settings import BaseSettings
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # 域名配置
    DOMAIN: str = "localhost"

    # 数据库
    DATABASE_URL: str = "sqlite:///./data/audio_drama.db"

    # 密钥
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_SECONDS: int = 1800

    # SSO 单点登录配置
    SSO_ENABLED: bool = True  # 是否启用 SSO 单点登录
    LOCAL_LOGIN_ENABLED: bool = False  # 是否启用本地登录（默认关闭，作为备用）
    SSO_JWT_AUTH_URL: str = "http://localhost:8000"  # jwt-auth 服务地址
    SSO_SECRET_KEY: str = "Ck-ZbtbR-sdSnQjUroh2q_-joNuUreJtfAnRnqeKFCJgaBvWRbHN6hKscrXxg9bP__KQ_Yl_sDFVu1iG1PlKHg"  # 与 jwt-auth 的 SECRET_KEY 一致
    SSO_ALGORITHM: str = "HS256"

    # 并发控制
    MAX_CONCURRENT_USERS: int = 10
    SESSION_EXPIRE_SECONDS: int = 1800

    # 文件上传
    UPLOAD_MAX_FILE_SIZE: int = 104857600  # 100MB
    STREAM_TOKEN_EXPIRE_SECONDS: int = 600

    # 媒体文件存储目录（支持绝对路径和相对路径）
    MEDIA_DIR: str = "media1/albums"

    # 默认管理员密码
    DEFAULT_ADMIN_PASSWORD: str = "123456"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
