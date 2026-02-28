# 极简广播剧系统 (Minimalist Radio Drama System)

一个极简高效的广播剧音频管理系统，支持专辑管理、音频上传、在线播放和用户认证。

## 功能特性

- 🎵 **音频管理** - 支持MP3/FLAC/OGG等格式，批量上传
- 📚 **专辑管理** - 创建专辑，管理封面，拖拽排序
- 🎧 **在线播放** - 流式播放，支持进度保存
- 👥 **用户认证** - JWT认证，角色管理（管理员/普通用户）
- 📱 **响应式设计** - 完美适配移动端和桌面端
- 🔒 **安全防护** - 流媒体令牌验证，防止盗链
- 🏗️ **部署简单** - Docker Compose一键部署

## 技术栈

### 后端
- FastAPI - 高性能异步框架
- SQLite - 轻量级数据库
- Redis - 会话管理和在线人数统计
- Docker - 容器化部署

### 前端
- Vue 3 - 渐进式框架
- TypeScript - 类型安全
- Vite - 构建工具
- Tailwind CSS - 原子化CSS

### 反向代理
- Caddy - 自动SSL证书管理

## 快速开始

### 前置要求

- Docker & Docker Compose
- Node.js 18+ (前端开发)
- Python 3.10+ (后端开发)

### 一键部署

```bash
git clone <repository-url>
cd audio-drama-system
docker-compose up -d
```

### 访问地址

- 前端: http://localhost:8000
- 后端API: http://localhost:8000/api
- API文档: http://localhost:8000/docs

### 默认账号

- 用户名: `admin`
- 密码: `123456`

## 开发指南

### 后端开发

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

## 目录结构

```
audio-drama-system/
├── backend/           # 后端代码
│   ├── app/
│   │   ├── api/      # API路由
│   │   ├── core/     # 核心配置
│   │   ├── db/       # 数据库
│   │   ├── models/   # 数据模型
│   │   └── main.py   # 应用入口
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/         # 前端代码
│   ├── src/
│   │   ├── api/      # API封装
│   │   ├── components/
│   │   ├── router/   # 路由配置
│   │   ├── stores/   # 状态管理
│   │   └── views/    # 页面组件
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## API接口

主要接口文档：http://localhost:8000/docs

### 认证
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户退出
- `POST /api/auth/heartbeat` - 心跳保活

### 专辑管理
- `GET /api/admin/albums` - 获取专辑列表
- `POST /api/admin/albums` - 创建专辑
- `GET /api/admin/albums/{id}` - 获取专辑详情
- `PUT /api/admin/albums/{id}` - 更新专辑
- `DELETE /api/admin/albums/{id}` - 删除专辑

### 剧集管理
- `GET /api/admin/albums/{id}/episodes` - 获取剧集列表
- `POST /api/admin/albums/{id}/episodes` - 创建剧集
- `DELETE /api/admin/episodes/{id}` - 删除剧集
- `POST /api/admin/episodes/{id}/upload` - 上传音频
- `POST /api/admin/albums/{id}/episodes/batch-upload` - 批量上传

### 音频流
- `GET /api/stream/token/{episode_id}` - 获取流媒体令牌
- `GET /api/stream/{episode_id}` - 音频流播放（需要令牌）

## 配置说明

后端环境变量 (`docker-compose.yml`):

```yaml
environment:
  - DATABASE_URL=sqlite:///./data/audio_drama.db
  - REDIS_URL=redis://redis:6379/0
  - SECRET_KEY=your-secret-key
  - JWT_SECRET_KEY=your-jwt-secret
  - MAX_CONCURRENT_USERS=10
  - SESSION_EXPIRE_SECONDS=1800
  - UPLOAD_MAX_FILE_SIZE=104857600
  - DEFAULT_ADMIN_PASSWORD=123456
```

## 部署到生产环境

### 使用Caddy自动SSL

1. 复制Caddy配置:
```bash
sudo cp Caddyfile /etc/caddy/Caddyfile
sudo systemctl restart caddy
```

2. 域名配置示例:
```
your-domain.com {
    reverse_proxy localhost:8000
}
```

### 使用Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /media {
        alias /path/to/media;
    }
}
```

## 注意事项

1. **安全**: 生产环境请修改默认密码和密钥
2. **存储**: 建议将/media目录挂载到持久化存储
3. **备份**: 定期备份SQLite数据库和媒体文件

## 许可证

MIT License

## 作者

琪琪 (Duoduo) - 音频爱好者 & 极客程序员

## 更新日志

### v1.0.0 (2026-02-28)
- ✅ 核心功能完成
- ✅ 前后端分离架构
- ✅ Docker部署支持
- ✅ 移动端响应式适配
- ✅ 零Element Plus依赖（纯原生实现）
