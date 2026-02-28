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
    """初始化数据库表"""
    from ..models.models import User, Album, Episode, Session

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    # 插入默认管理员
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            # 使用预计算的bcrypt hash for "123456" 避免passlib初始化问题
            hashed_password = "$2b$12$tN.2A6HaFzJzwt8TOWqtkOL9QqTis85DCHcpj2Q2nYUaqDatMwRHW"

            admin = User(
                username="admin",
                password_hash=hashed_password,
                role="admin"
            )
            db.add(admin)
            db.commit()
            print(f"✅ 默认管理员账号已创建: admin / 123456")
        else:
            print("✅ 数据库已存在，跳过初始化")
    finally:
        db.close()
