import os
from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import FileResponse
from sqlalchemy.orm import Session
from sso_client import create_sso_router
from app.db.base import get_db, init_db
from app.core.config import settings
from app.api import albums, episodes, upload, stream

# 创建 SSO 客户端（使用与 jwt-auth 共享的密钥）
sso = create_sso_router(
    secret_key=settings.SSO_SECRET_KEY,
    jwt_auth_url=settings.SSO_JWT_AUTH_URL,
    jwt_expire_seconds=settings.JWT_EXPIRE_SECONDS,
    algorithm=settings.SSO_ALGORITHM,
    sso_enabled=settings.SSO_ENABLED,
)

# 创建 FastAPI 应用
app = FastAPI(
    title="极简广播剧管理系统 API",
    description="极简广播剧管理与在线收听系统的后端 API",
    version="1.0.0"
)

# 创建 SSO 客户端（使用与 jwt-auth 共享的密钥）
sso = create_sso_router(
    secret_key=settings.SSO_SECRET_KEY,
    jwt_auth_url=settings.SSO_JWT_AUTH_URL,
    jwt_expire_seconds=settings.JWT_EXPIRE_SECONDS,
    algorithm=settings.SSO_ALGORITHM,
    sso_enabled=settings.SSO_ENABLED,
)

# CORS 中间件 - 智能配置
# 根据环境智能选择CORS策略
import os
from urllib.parse import urlparse

def get_cors_config():
    """获取CORS配置 - 支持多种场景"""
    env = os.getenv("ENV", "development").lower()
    origins_str = os.getenv("ALLOW_ORIGINS", "")
    
    # 策略1: 明确指定来源 (推荐生产环境)
    if origins_str:
        allow_origins = [origin.strip() for origin in origins_str.split(",")]
        print(f"✅ CORS 已配置明确域名: {allow_origins}")
        return allow_origins
    
    # 策略2: 开发环境 - 仅允许本地前端
    if env == "development":
        allow_origins = [
            "http://localhost:5173",      # Nuxt dev server
            "http://127.0.0.1:5173",
            "http://localhost:3000",      # 备选端口
            "http://127.0.0.1:3000",
        ]
        print(f"✅ CORS 已配置开发环境: {allow_origins}")
        return allow_origins
    
    # 策略3: 生产环境 - 同域部署（前端已集成到后端）
    # 此时无需CORS，因为都来自同一域名
    print("✅ CORS 已禁用: 生产环境同域部署模式")
    return []  # 空列表 = 仅允许同域

cors_config = get_cors_config()

if cors_config:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],  # 下载文件时暴露headers
        max_age=3600,  # preflight缓存1小时
    )

# 注册路由
app.include_router(sso.router, prefix="/api")
app.include_router(albums.router, prefix="/api/admin")
app.include_router(episodes.router, prefix="/api/admin")
app.include_router(upload.router, prefix="/api/admin")
app.include_router(stream.router, prefix="/api")

# 静态文件服务（SPA 前端）- 使用中间件方式，避免覆盖 API 路由
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")

class SPAMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path

        # 跳过 API 路径
        if path.startswith("/api"):
            return await call_next(request)

        # 处理静态资源
        if path.startswith("/_nuxt/"):
            file_path = os.path.join(static_dir, "_nuxt", path[7:])
            if os.path.exists(file_path):
                return FileResponse(file_path)

        if path.startswith("/static/"):
            file_path = os.path.join(static_dir, path[8:])
            if os.path.exists(file_path):
                return FileResponse(file_path)

        # SPA fallback - 返回 index.html
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

        return await call_next(request)

if os.path.exists(static_dir):
    app.add_middleware(SPAMiddleware)
    print(f"✅ 已添加 SPA 中间件，静态目录：{static_dir}")
else:
    print(f"⚠️  静态文件目录不存在：{static_dir}，前端将不可用")


# 健康检查
@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "service": "audio-drama-backend",
        "version": "1.0.0"
    }


# 在线人数查询（使用 JWT token 验证）
@app.get("/api/online")
async def get_online_count(request: Request):
    """获取当前在线人数（需要认证）"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return {
            "success": True,
            "data": {
                "current_online": 0,
                "max_online": settings.MAX_CONCURRENT_USERS
            }
        }
    return {
        "success": True,
        "data": {
            "current_online": 0,
            "max_online": settings.MAX_CONCURRENT_USERS
        }
    }


# 系统状态（使用 JWT token 验证）
@app.get("/api/system/status")
async def system_status(request: Request, db: Session = Depends(get_db)):
    """系统状态（需要认证）"""
    from sqlalchemy import func
    from app.models.models import Album, Episode

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return {
            "success": True,
            "data": {
                "total_albums": 0,
                "total_episodes": 0,
                "storage_used_mb": 0
            }
        }

    # 使用 contextmanager 方式，确保异常时连接也会释放
    total_albums = db.query(func.count(Album.id)).scalar()
    total_episodes = db.query(func.count(Episode.id)).scalar()

    # 存储空间
    media_dir = os.path.abspath(settings.MEDIA_DIR)
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
            "total_albums": total_albums or 0,
            "total_episodes": total_episodes or 0,
            "storage_used": total_size,
            "storage_used_mb": round(total_size / 1024 / 1024, 2)
        }
    }


# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP 异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    import traceback
    error_detail = traceback.format_exc()
    print(f"未捕获的异常：{error_detail}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "error": "内部服务器错误"}
    )


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    print("🚀 正在初始化应用...")
    try:
        init_db()
    except Exception as e:
        print(f"❌ 数据库初始化失败：{e}")
        raise
    print("✅ 应用初始化完成")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
