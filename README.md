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

### 环境要求

- Python 3.10+
- Node.js 18+

### 1. 后端部署

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（创建表、索引、默认管理员）
./init.sh

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. 前端构建

```bash
cd backend

# 构建前端静态文件（自动设置 API 地址为相对路径）
./build-frontend.sh

# 重启后端服务（加载新的静态文件）
pkill -f "uvicorn app.main:app"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

访问 http://localhost:8000

## 🔑 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | 123456 | 管理员 |

⚠️ **首次登录后请立即修改密码！**

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
│   ├── build-frontend.sh # 前端构建脚本
│   └── requirements.txt
├── nuxt-frontend/       # Nuxt 3 前端源码
│   ├── .output/public/  # 静态构建输出
│   ├── app.config.ts    # 应用配置（API 地址）
│   └── package.json
├── media/               # 音频文件存储
│   └── albums/          # 按专辑 ID 存储
└── docs/                # 文档
```

## 📖 API 文档

启动后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📋 主要 API

### 认证
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/logout` | POST | 用户登出 |
| `/api/auth/heartbeat` | POST | 心跳保活 |

### 专辑管理
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/admin/albums` | GET | 获取专辑列表 |
| `/api/admin/albums` | POST | 创建专辑 |
| `/api/admin/albums/{id}` | GET | 获取专辑详情 |
| `/api/admin/albums/{id}` | PUT | 更新专辑 |
| `/api/admin/albums/{id}` | DELETE | 删除专辑 |

### 音频管理
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/admin/albums/{id}/episodes` | GET | 获取剧集列表 |
| `/api/admin/albums/{id}/episodes` | POST | 创建剧集 |
| `/api/admin/albums/{id}/episodes/batch-upload` | POST | 批量上传音频 |
| `/api/admin/episodes/{id}` | PUT | 更新剧集 |
| `/api/admin/episodes/{id}` | DELETE | 删除剧集 |

### 音频流
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/stream/{episode_id}` | GET | 获取音频流 |
| `/api/stream/token/{episode_id}` | GET | 获取流 Token |

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | FastAPI + SQLAlchemy |
| 数据库 | SQLite |
| 前端 | Nuxt 3 + Vue 3 + TailwindCSS |
| 认证 | JWT + Bcrypt |
| 音频处理 | Mutagen |

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

# 查看进程
ps aux | grep uvicorn

# 停止服务
pkill -f "uvicorn app.main:app"

# 查看日志
tail -f /tmp/uvicorn.log
```

## 📂 音频文件存储

上传的音频文件存储在 `/media/albums/` 目录下：

```
/media/albums/
├── 1/                    # 专辑 ID
│   ├── uuid-xxx.mp3      # 音频文件
│   └── uuid-yyy.mp3
└── 2/
    └── uuid-zzz.mp3
```

本地开发时，可以创建软链接到项目目录：
```bash
ln -s /root/audio-drama-system/media /media
```

## 🔒 安全建议

1. **修改默认密码** - 首次登录后立即修改 admin 密码
2. **防火墙配置** - 仅开放必要端口（如 8000）
3. **定期备份** - 每天备份数据库和音频文件
4. **HTTPS** - 生产环境建议使用 Nginx 反向代理配置 HTTPS

## 📄 License

MIT License
