# 极简广播剧管理与在线收听系统

一个轻量级的广播剧管理与在线收听平台，支持专辑管理、音频上传、在线播放等功能。

## ✨ 特性

- 🎵 **专辑管理** - 创建、编辑、删除专辑
- 📁 **批量上传** - 支持多音频文件批量上传
- 🎧 **在线播放** - 基于 Token 的流式播放，防下载
- 🔐 **用户认证** - JWT Token 鉴权，Session 管理
- 📊 **数据统计** - 在线人数、存储空间统计
- 📱 **响应式** - 适配移动端和桌面端

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- Node.js 18+

### 2. 后端部署

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
./init.sh

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. 前端构建

```bash
cd backend

# 构建前端静态文件
./build-frontend.sh

# 重启后端服务（加载静态文件）
pkill -f "uvicorn app.main:app"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000

## 🔑 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | 123456 | 管理员 |

⚠️ 首次登录后请立即修改密码！

## 📁 项目结构

```
audio-drama-system/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心配置
│   │   ├── db/          # 数据库模块
│   │   ├── models/      # 数据模型
│   │   └── main.py      # 应用入口
│   ├── data/            # SQLite 数据库
│   ├── static/          # 前端静态文件
│   ├── init.sh          # 初始化脚本
│   └── requirements.txt
├── nuxt-frontend/       # Nuxt 3 前端源码
│   ├── .output/public/  # 静态构建输出
│   └── package.json
├── media/               # 音频文件存储
└── docs/                # 文档
```

## 📖 API 文档

启动后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📋 主要 API

### 认证
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `POST /api/auth/heartbeat` - 心跳保活

### 专辑管理
- `GET /api/admin/albums` - 获取专辑列表
- `POST /api/admin/albums` - 创建专辑
- `PUT /api/admin/albums/{id}` - 更新专辑
- `DELETE /api/admin/albums/{id}` - 删除专辑

### 音频管理
- `GET /api/admin/albums/{id}/episodes` - 获取剧集列表
- `POST /api/admin/albums/{id}/episodes/batch-upload` - 批量上传音频

### 音频流
- `GET /api/stream/{episode_id}` - 获取音频流
- `GET /api/stream/token/{episode_id}` - 获取流 Token

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | FastAPI + SQLAlchemy |
| 数据库 | SQLite |
| 前端 | Nuxt 3 + Vue 3 |
| 认证 | JWT + Bcrypt |

## 📝 文档

- [修复总结与部署方案](docs/FIX_SUMMARY.md)
- [产品需求文档](docs/PRD.md)
- [技术方案文档](docs/TSD.md)
- [开发计划](docs/DEVELOPMENT_PLAN.md)

## 🔧 运维命令

```bash
# 启动后端
cd backend && source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 构建前端
cd backend && ./build-frontend.sh

# 初始化数据库
cd backend && ./init.sh

# 备份数据库
cp backend/data/audio_drama.db backup/audio_drama_$(date +%Y%m%d).db
```

## 📄 License

MIT License
