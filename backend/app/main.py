from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.db.base import get_db, init_db
from app.core.config import settings
from app.api import auth, albums, episodes, upload, stream

# 创建FastAPI应用
app = FastAPI(
    title="极简广播剧管理系统API",
    description="极简广播剧管理与在线收听系统的后端API",
    version="1.0.0"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://q.1006868.xyz"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(albums.router, prefix="/api/admin")
app.include_router(episodes.router, prefix="/api/admin")
app.include_router(upload.router, prefix="/api/admin")
app.include_router(stream.router, prefix="/api")


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "service": "audio-drama-backend",
        "version": "1.0.0"
    }


# 在线人数查询
@app.get("/api/online")
async def get_online_count():
    """获取当前在线人数"""
    from app.core.redis_client import get_current_online_count
    count = await get_current_online_count()
    return {
        "success": True,
        "data": {
            "current_online": count,
            "max_online": settings.MAX_CONCURRENT_USERS
        }
    }


# 系统状态
@app.get("/api/system/status")
async def system_status():
    """系统状态"""
    from app.core.redis_client import get_current_online_count
    from sqlalchemy import func
    from app.models.models import Album, Episode
    import os

    online_count = await get_current_online_count()

    # 统计专辑和剧集数量
    db = next(get_db())
    try:
        total_albums = db.query(func.count(Album.id)).scalar()
        total_episodes = db.query(func.count(Episode.id)).scalar()
    finally:
        db.close()

    # 存储空间
    media_dir = "/media/albums"
    if os.path.exists(media_dir):
        total_size = sum(
            os.path.getsize(os.path.join(dirpath, filename))
            for dirpath, _, filenames in os.walk(media_dir)
            for filename in filenames
        )
    else:
        total_size = 0

    return {
        "success": True,
        "data": {
            "online_count": online_count,
            "max_online": settings.MAX_CONCURRENT_USERS,
            "total_albums": total_albums or 0,
            "total_episodes": total_episodes or 0,
            "storage_used": total_size,
            "storage_used_mb": round(total_size / 1024 / 1024, 2)
        }
    }


# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    import traceback
    error_detail = traceback.format_exc()
    print(f"未捕获的异常: {error_detail}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "error": "内部服务器错误"}
    )


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    print("🚀 正在初始化应用...")

    # 初始化数据库
    try:
        init_db()
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        raise

    print("✅ 应用初始化完成")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
