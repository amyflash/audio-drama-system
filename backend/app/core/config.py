from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 域名配置
    DOMAIN: str = "localhost"

    # 数据库
    DATABASE_URL: str = "sqlite:///./data/audio_drama.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # 密钥
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_SECONDS: int = 1800

    # 并发控制
    MAX_CONCURRENT_USERS: int = 10
    SESSION_EXPIRE_SECONDS: int = 1800

    # 文件上传
    UPLOAD_MAX_FILE_SIZE: int = 104857600  # 100MB
    STREAM_TOKEN_EXPIRE_SECONDS: int = 600

    # 默认管理员密码
    DEFAULT_ADMIN_PASSWORD: str = "123456"


settings = Settings()
