from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


# 数据库URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/audio_drama.db")

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False
)

# Session工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表（仅 Album 和 Episode）"""
    from ..models.models import Album, Episode

    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表已创建")
