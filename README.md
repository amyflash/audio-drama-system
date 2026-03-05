# 极简广播剧系统 (Minimalist Radio Drama System)

一个极简高效的广播剧音频管理系统，支持专辑管理、音频上传、在线播放和用户认证。

---

## 目录

- [项目背景与目标](#项目背景与目标)
- [功能特性](#功能特性)
- [用户角色与权限](#用户角色与权限)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [开发指南](#开发指南)
- [API接口](#api接口)
- [部署说明](#部署说明)
- [技术方案细节](#技术方案细节)

---

## 项目背景与目标

为了实现广播剧专辑资源的统一管理及受控分发，本项目旨在构建一个轻量级的 Web 系统。管理员可便捷地上传音频资源，授权用户（普通用户）仅可在线收听，严禁下载，且系统需严格控制同时在线人数上限，以保证带宽成本和版权保护。

### 核心目标

- 🎵 统一的音频资源管理平台
- 👥 基于角色的访问控制（管理员/普通用户）
- 🔒 防盗链和防下载机制
- 👥 在线并发人数限制（默认10人）
- 📱 完美适配移动端和桌面端

---

## 功能特性

### 管理员功能

- 📚 **专辑管理**
  - 创建、编辑、删除专辑
  - 专辑搜索（标题/描述）
  - 封面图上传
  - 专辑描述管理

- 🎧 **音频管理**
  - 批量上传音频文件
  - 支持MP3/FLAC/OGG等格式
  - 剧集标题编辑
  - 剧集排序
  - 删除剧集
  - 剧集搜索

- 👥 **用户管理**
  - 查看在线用户状态
  - 控制并发人数

### 普通用户功能

- 🔐 **用户认证**
  - 登录/注销
  - Token 自动刷新

- 📚 **音频浏览**
  - 浏览所有公开专辑
  - 查看专辑详情
  - 查看剧集列表

- 🎧 **在线播放**
  - 流式播放音频
  - 播放/暂停控制
  - 快进/快退（10秒）
  - 播放进度条
  - 缓冲进度条
  - 进度自动保存

### 系统特性

- 📱 **响应式设计**
  - 完美适配移动端和桌面端

- 🔒 **安全防护**
  - 流媒体令牌验证，防止盗链

- 🎨 **绿色主题**
  - 保护视力的清新UI设计

- 🏗️ **部署简单**
  - Docker Compose一键部署
  - 无需额外依赖（SQLite 作为唯一数据存储）

- ⚡ **高性能**
  - Nuxt 3 SSR优化，FastAPI异步处理

- 🎛️ **进程管理**
  - PM2自动重启，稳定运行

---

## 用户角色与权限

| 角色 | 描述 | 权限范围 |
| :--- | :--- | :--- |
| **Admin (管理员)** | 系统所有者 | 专辑/音频的增删改查、批量上传、资源管理、查看系统状态 |
| **User (普通用户)** | 授权听众 | 登录系统、浏览专辑列表、在线播放音频。**无下载权限，无管理权限** |
| **Visitor (访客)** | 未登录用户 | 仅可访问登录页。若尝试访问内容或播放，将被强制跳转至登录页 |

---

## 技术栈

### 后端

- **FastAPI** - 高性能异步框架
- **SQLite** - 轻量级数据库（同时用于数据存储和会话管理）
- **Docker** - 容器化部署
- **Python 3.10+** - 开发语言

### 前端

- **Nuxt 3** - Vue 3 元框架
- **Vue 3** - 渐进式框架
- **TypeScript** - 类型安全
- **Pinia** - 状态管理
- **Tailwind CSS** - 原子化CSS
- **Axios** - HTTP 客户端
- **PM2** - 进程管理
- **Node.js 22+** - 运行环境

### 反向代理

- **Caddy** - 自动SSL证书管理（生产环境）

---

## 快速开始

### 前置要求

- Docker & Docker Compose
- Node.js 22+ (前端开发)
- Python 3.10+ (后端开发)

### 一键部署

```bash
git clone https://github.com/amyflash/audio-drama-system.git
cd audio-drama-system
docker-compose up -d
```

### 前端开发模式

```bash
cd nuxt-frontend
npm install
npm run dev
# 访问 http://localhost:5173
重新构建并部署：

     1    # 构建前端镜像
     2    cd nuxt-frontend
     3    docker build -t audio-drama-system_nuxt-frontend:latest .
     4
     5    # 启动所有服务
     6    docker-compose up -d
```

### 后端开发模式

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# 在线人数限制和会话管理正常工作
```

### PM2 管理（生产环境）

```bash
# 启动 Nuxt 前端
cd /home/duoduo/.openclaw/workspace/audio-drama-system
pm2 start ecosystem-nuxt.config.js
pm2 save

# 查看状态
pm2 status

# 查看日志
pm2 logs audio-drama-nuxt
```

### 访问地址

- **前端**: http://localhost:5173 (开发) / https://q.1006868.xyz (生产)
- **后端API**: http://localhost:8000 (开发) / https://h.1006868.xyz (生产)
- **API文档**: http://localhost:8000/docs (开发) / https://h.1006868.xyz/docs (生产)

### 默认账号

- **用户名**: `admin`
- **密码**: `123456`
- **角色**: 管理员

---

## 开发指南

### 项目结构

```
audio-drama-system/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/             # API 路由
│   │   │   ├── auth.py      # 认证接口
│   │   │   ├── albums.py    # 专辑管理
│   │   │   ├── episodes.py  # 剧集管理
│   │   │   └── stream.py    # 音频流接口
│   │   ├── core/            # 核心配置
│   │   │   ├── config.py    # 配置文件
│   │   │   ├── security.py  # 安全模块
│   │   │   └── session_crud.py # 会话管理
│   │   ├── db/              # 数据库
│   │   ├── models/          # 数据模型
│   │   └── main.py          # 应用入口（已添加静态文件服务）
│   ├── requirements.txt
│   └── Dockerfile
├── nuxt-frontend/           # Nuxt 3 前端
│   ├── pages/               # 页面路由
│   │   ├── login.vue        # 登录页
│   │   ├── index.vue        # 专辑列表
│   │   ├── albums/
│   │   │   └── [id].vue     # 专辑详情
│   │   └── player/
│   │       └── [id].vue     # 播放器
│   ├── plugins/             # Nuxt 插件
│   │   └── api.ts           # Axios API 封装
│   ├── api/                 # API 模块
│   ├── stores/              # Pinia 状态管理
│   ├── nuxt.config.ts       # Nuxt 配置（已配置为静态生成）
│   └── package.json
├── Dockerfile.combined      # 集成构建 Dockerfile（前后端整合）
├── docker-compose.yml       # 容器编排配置（已更新为单服务）
├── ecosystem-nuxt.config.js # PM2 配置（用于传统部署）
├── start-nuxt.sh            # Nuxt 启动脚本（用于传统部署）
└── README.md
```

### 后端依赖安装

```bash
cd backend
pip install -r requirements.txt
```

主要依赖：

- fastapi - Web 框架
- uvicorn - ASGI 服务器
- sqlalchemy - ORM
- python-jose - JWT 处理
- mutagen - 音频元数据解析
- passlib - 密码哈希

### 前端依赖安装

```bash
cd nuxt-frontend
npm install
```

主要依赖：

- nuxt - Nuxt 3 框架
- vue - Vue 3
- pinia - 状态管理
- axios - HTTP 客户端
- @nuxtjs/tailwindcss - Tailwind CSS 集成

---

## API接口

详细 API 文档：http://localhost:8000/docs

### 认证接口

- `POST /api/auth/login` - 用户登录（含并发控制）
- `POST /api/auth/logout` - 用户退出（清除会话）
- `POST /api/auth/heartbeat` - 心跳保活（刷新会话过期时间）
- `GET /api/auth/me` - 获取当前用户信息

### 专辑管理（管理员）

- `GET /api/admin/albums` - 获取专辑列表
- `POST /api/admin/albums` - 创建专辑
- `GET /api/admin/albums/{id}` - 获取专辑详情
- `PUT /api/admin/albums/{id}` - 更新专辑
- `DELETE /api/admin/albums/{id}` - 删除专辑

### 剧集管理（管理员）

- `GET /api/admin/albums/{id}/episodes` - 获取剧集列表
- `POST /api/admin/albums/{id}/episodes` - 创建剧集
- `GET /api/admin/episodes/{id}` - 获取剧集详情
- `PUT /api/admin/episodes/{id}` - 更新剧集
- `DELETE /api/admin/episodes/{id}` - 删除剧集
- `POST /api/admin/episodes/{id}/upload` - 上传音频文件
- `POST /api/admin/albums/{id}/episodes/batch-upload` - 批量上传音频

### 音频流（用户）

- `GET /api/stream/token/{episode_id}` - 获取流媒体令牌（10分钟有效期）
- `GET /api/stream/{episode_id}` - 音频流播放（需要令牌认证）

---

## 部署说明

### Docker Compose 部署

```bash
docker-compose up -d
```

### 单容器部署（前后端整合）

本项目现在支持将前端打包成静态文件，直接挂载到 FastAPI 后端，实现单容器部署。这种方法简化了部署架构，无需单独的前端服务器，也无需处理跨域问题。

**修改说明：**
- 前端（Nuxt 3）配置为静态生成（SSG）
- FastAPI 后端添加静态文件服务，支持 SPA 路由
- 创建了集成构建的 Dockerfile.combined
- 更新了 docker-compose.yml 使用单服务架构

**部署步骤：**

1. **上传文件到服务器**
   ```bash
   # 将修改后的整个项目上传到服务器
   scp -r audio-drama-system user@your-server:/path/to/
   ```

2. **构建并启动容器**
   ```bash
   cd /path/to/audio-drama-system
   docker-compose up -d --build
   ```

3. **验证部署**
   - 访问前端：http://your-server:8000
   - 访问API文档：http://your-server:8000/docs
   - 健康检查：http://your-server:8000/api/health

**优势：**
- 简化架构：只有一个容器需要管理
- 避免跨域：前后端同源，无需 CORS 配置
- 统一入口：所有请求通过同一个端口访问
- 易于维护：日志、监控、备份更简单

### 环境变量配置

后端环境变量 (`docker-compose.yml`):

```yaml
environment:
  - DATABASE_URL=sqlite:///./data/audio_drama.db
  - SECRET_KEY=your-secret-key
  - JWT_SECRET_KEY=your-jwt-secret
  - MAX_CONCURRENT_USERS=10
  - SESSION_EXPIRE_SECONDS=1800
  - UPLOAD_MAX_FILE_SIZE=104857600 # 100MB
  - DEFAULT_ADMIN_PASSWORD=123456
```

### 使用 Caddy 自动 SSL

1. 复制 Caddy 配置:

```bash
sudo cp Caddyfile /etc/caddy/Caddyfile
sudo systemctl restart caddy
```

2. 域名配置示例:

```
q.1006868.xyz {
    reverse_proxy localhost:5173
}

h.1006868.xyz {
    reverse_proxy localhost:8000
}
```

### PM2 生产部署

```bash
# 安装 PM2
npm install -g pm2

# 启动 Nuxt 前端
cd audio-drama-system
pm2 start ecosystem-nuxt.config.js

# 保存 PM2 配置
pm2 save

# 设置开机自启
pm2 startup systemd
```

---

## 技术方案细节

### 1. 并发控制（10人限制）

利用 SQLite 数据库的 `sessions` 表实现会话管理和并发控制：

**存储结构**：
- 表: `sessions`
- 字段: `id`, `user_id`, `token`, `ip_address`, `user_agent`, `expires_at`

**登录校验流程**：
1. 请求到达 `/api/auth/login`
2. 查询 `sessions` 表中 `expires_at > 当前时间` 的记录数
3. 若用户不在线且总数 >= 10，返回 HTTP 403
4. 否则，校验密码通过后，创建新的 session 记录

**心跳保活**：
- 前端每隔 15 分钟请求一次 `/api/auth/heartbeat`
- 后端更新 session 的 `expires_at` 字段，延长过期时间

### 2. 防下载音频流方案

**核心原则**：物理文件路径不以公开 URL 形式直接暴露，而是通过动态 API 代理：

**API 定义**：
- `GET /api/stream/{episode_id}`

**后端逻辑**：
1. 接收请求，验证 Token 有效性
2. 根据 `episode_id` 查库得到物理路径
3. 使用 `FileResponse(path, media_type='audio/mpeg')` 返回文件流
4. 支持断点续传（Range 请求）

**前端逻辑**：
1. 播放器加载前，调用 `/api/stream/token/{episode_id}` 获取临时 Token
2. 在音频 URL 中添加 Token 参数：`?token=xxx`
3. Token 有效期 10 分钟，绑定 user_id 和 episode_id

**结果**：
- 用户只能通过带 Token 的 API 获取流
- 浏览器无法执行"另存为"（URL 是动态逻辑的）
- Token 失效即断流

### 3. 数据库设计

#### 数据表结构

- **user (用户表)**
  - `id` (PK, Int): 自增ID
  - `username` (Varchar): 登录账号
  - `password_hash` (Varchar): 密码哈希
  - `role` (Varchar): 'admin' 或 'user'
  - `is_superuser` (Boolean): 是否超级用户

- **album (专辑表)**
  - `id` (PK, Int): 专辑ID
  - `title` (Varchar): 专辑名
  - `cover_image` (Varchar): 封面图路径
  - `description` (Text): 简介
  - `episode_count` (Int): 剧集数量
  - `created_at` (Datetime): 创建时间
  - `updated_at` (Datetime): 更新时间

- **episode (单集表)**
  - `id` (PK, Int): 单集ID
  - `album_id` (FK, Int): 所属专辑ID
  - `title` (Varchar): 标题
  - `file_path` (Varchar, nullable): 服务器存储路径
  - `file_size` (Int): 文件大小（字节）
  - `duration` (Int): 时长（秒）
  - `sort_order` (Int): 排序权重
  - `created_at` (Datetime): 创建时间

- **session (会话表)**
  - `id` (PK, Int): 会话ID
  - `user_id` (FK, Int): 用户ID
  - `token` (Varchar): 会话令牌
  - `ip_address` (Varchar): IP 地址
  - `user_agent` (Text): User Agent
  - `expires_at` (Datetime): 过期时间

---

## 安全注意事项

1. **生产环境安全**
   - 修改默认密码和密钥
   - 启用 HTTPS（Caddy 自动配置）
   - 定期备份数据库和媒体文件
   - 限制文件上传大小

2. **存储建议**
   - 将 `/media` 目录挂载到持久化存储
   - 定期清理过期的会话记录

3. **备份策略**
   - 定期备份 SQLite 数据库文件
   - 备份音频文件目录

---

## 更新日志

### v2.2.0 (2026-03-05)
- ✅ **前后端整合部署** - 前端打包成静态文件挂载到 FastAPI 后端
- ✅ **单容器架构** - 简化部署，无需单独前端容器
- ✅ **静态生成优化** - Nuxt 配置为静态 SPA 模式
- ✅ **路由统一处理** - FastAPI 同时服务 API 和前端页面

### v2.1.0 (2026-03-03)
- ✅ **移除 Redis 依赖** - 使用 SQLite 统一管理数据和会话
- ✅ **简化部署** - 无需额外依赖，降低运维复杂度

### v2.0.0 (2026-03-01)
- ✅ **前端迁移至 Nuxt 3** - 从 Vite 迁移到 Nuxt 3 框架
- ✅ **专辑管理增强** - 新增搜索、编辑、删除功能
- ✅ **剧集管理增强** - 新增搜索、编辑、删除功能
- ✅ **UI 优化** - 绿色主题设计，左滑显示操作按钮
- ✅ **音频流认证** - Token 机制，防止盗链下载
- ✅ **PM2 管理** - 进程自动重启，稳定运行
- ✅ **修复音频播放** - 解决 401 认证问题
- ✅ **移动端优化** - 完美响应式适配

### v1.0.0 (2026-02-28)
- ✅ 核心功能完成
- ✅ 前后端分离架构
- ✅ Docker 部署支持
- ✅ 移动端响应式适配
- ✅ 零外部UI依赖（纯原生实现）

---

## 许可证

MIT License

---

## 作者

**琪琪 (Duoduo)**
- 音频爱好者 & 极客程序员
- GitHub: [@amyflash](https://github.com/amyflash)
- 项目: [极简广播剧系统](https://github.com/amyflash/audio-drama-system)

---

## 致谢

感谢所有为开源社区做出贡献的开发者！
