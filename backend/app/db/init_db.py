#!/usr/bin/env python3
"""
SQLite 数据库初始化脚本
用于手动初始化或重置数据库

使用方法:
    python -m app.db.init_db
    或
    python app/db/init_db.py
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from app.db.base import engine, SessionLocal, Base
from app.models.models import User
import bcrypt


def create_tables():
    """创建所有数据库表"""
    print("📦 正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")


def create_default_admin():
    """创建默认管理员账号"""
    print("👤 正在创建默认管理员账号...")
    
    db = SessionLocal()
    try:
        # 检查是否已存在管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("⚠️  管理员账号已存在，跳过创建")
            return
        
        # 生成密码哈希 (密码：123456)
        password = "123456"
        salt = bcrypt.gensalt(rounds=12)
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        # 创建管理员
        admin = User(
            username="admin",
            password_hash=hashed_password,
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        
        print("✅ 默认管理员账号已创建")
        print("   用户名：admin")
        print("   密码：123456")
        print("⚠️  警告：请在登录后立即修改密码！")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 创建管理员失败：{e}")
        raise
    finally:
        db.close()


def create_indexes():
    """创建数据库索引"""
    print("📇 正在创建索引...")
    
    db = SessionLocal()
    try:
        # 使用原生 SQL 创建索引
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_albums_sort_order ON albums(sort_order)",
            "CREATE INDEX IF NOT EXISTS idx_albums_created_at ON albums(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_episodes_album_id ON episodes(album_id)",
            "CREATE INDEX IF NOT EXISTS idx_episodes_sort_order ON episodes(sort_order)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)",
        ]
        
        for sql in indexes:
            db.execute(text(sql))
        
        db.commit()
        print("✅ 索引创建完成")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 创建索引失败：{e}")
        raise
    finally:
        db.close()


def create_views():
    """创建数据库视图"""
    print("🔍 正在创建视图...")
    
    db = SessionLocal()
    try:
        # 专辑详情视图
        view_sql = """
        CREATE VIEW IF NOT EXISTS album_detail AS
        SELECT
            a.id,
            a.title,
            a.cover_image,
            a.description,
            a.sort_order,
            a.episode_count,
            a.created_at,
            a.updated_at,
            COALESCE(SUM(e.duration), 0) as total_duration
        FROM albums a
        LEFT JOIN episodes e ON a.id = e.album_id
        GROUP BY a.id
        """
        db.execute(text(view_sql))
        db.commit()
        print("✅ 视图创建完成")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 创建视图失败：{e}")
        raise
    finally:
        db.close()


def init_db():
    """完整初始化数据库"""
    print("=" * 50)
    print("🎵 极简广播剧系统 - 数据库初始化")
    print("=" * 50)
    
    # 确保数据目录存在
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)
    print(f"📁 数据目录：{data_dir}")
    
    # 创建表
    create_tables()
    
    # 创建索引
    create_indexes()
    
    # 创建视图
    create_views()
    
    # 创建默认管理员
    create_default_admin()
    
    print("=" * 50)
    print("✅ 数据库初始化完成！")
    print("=" * 50)


def reset_db():
    """重置数据库（删除所有数据）"""
    print("⚠️  警告：即将重置数据库，所有数据将被删除！")
    confirm = input("确认重置？(yes/no): ")
    
    if confirm.lower() != "yes":
        print("❌ 操作已取消")
        return
    
    db = SessionLocal()
    try:
        # 删除所有表
        Base.metadata.drop_all(bind=engine)
        print("✅ 已删除所有表")
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ 重置失败：{e}")
        raise
    finally:
        db.close()
    
    # 重新初始化
    init_db()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SQLite 数据库初始化工具")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="重置数据库（删除所有数据后重新初始化）"
    )
    
    args = parser.parse_args()
    
    if args.reset:
        reset_db()
    else:
        init_db()
