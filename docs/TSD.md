# 极简广播剧管理与在线收听系统
# 系统技术方案设计文档 (TSD)

**项目名称：** 极简广播剧管理与在线收听系统
**版本号：** V1.0.0
**技术负责人：** AI Assistant
**文档编写日期：** 2026-02-28
**文档状态：** 正式发布

---

## 1. 总体技术架构

### 1.1 架构概述

系统采用 **前后端分离 + B/S 架构**，使用 Docker Compose 进行容器化编排，实现轻量级、易部署的设计目标。

```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                             │
│                    (Vue3 + APlayer)                          │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                      Nginx (反向代理)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ 静态资源分发 │  │ API 代理     │  │ 音频流代理      │   │
│  │ /static/*    │  │ /api/*       │  │ /api/stream/*    │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI 后端服务                           │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌────────┐  │
│  │ 鉴权模块 │   │ 文件模块 │   │ Session  │   │  业务  │  │
│  │ JWT/Token │   │ 上传/存储│   │ Redis   │   │  逻辑  │  │
│  └──────────┘   └──────────┘   └──────────┘   └────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴──────────┐
         ↓                      ↓
┌────────────────┐   ┌────────────────────────────────┐
│  SQLite 数据库 │   │  Redis 缓存                   │
│  (用户/专辑/音频)│  │  - Session 管理               │
│                │  │  - 并发控制                    │
│                │  │  - 防盗链 Token                │
└────────────────┘   └────────────────────────────────┘
```

### 1.2 技术栈选型

| 层级 | 组件 | 版本/说明 |
| :--- | :--- | :--- |
| **前端** | Vue 3 | 使用 Composition API，响应式开发 |
| | Element Plus | UI 组件库 |
| | APlayer | 音频播放器 |
| | Pinia | 状态管理 |
| **后端** | FastAPI | 高性能异步 Web 框架 |
| | Pydantic | 数据验证 |
| | uvicorn | ASGI 服务器 |
| **数据库** | SQLite 3 | 轻量级关系型数据库 |
| **缓存** | Redis 7.x | Session 管理、并发控制 |
| **反向代理** | Nginx 1.24 | 流量转发、静态资源 |
| **容器化** | Docker | 容器镜像构建 |
| | Docker Compose | 服务编排 |

### 1.3 为什么选择这个技术栈？

**选择理由：**

- **Vue 3 + Element Plus**：成熟稳定，开发效率高，社区活跃
- **FastAPI**：
  - 原生异步支持，性能优于 Flask/Django
  - 自动生成 API 文档（Swagger UI）
  - 类型提示 + Pydantic 验证，减少 Bug
- **SQLite**：
  - 无需额外安装，零配置
  - 适合单机部署，满足百级数据量
- **Redis**：
  - 高性能缓存，支持 TTL 自动过期
  - 原子操作保证并发控制准确性

---

## 2. 数据库设计

### 2.1 数据表设计

#### 表 1: `users` - 用户表

| 字段名 | 类型 | 约束 | 说明 |
| :--- | :--- | :--- | :--- |
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 用户 ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 登录用户名 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希（bcrypt） |
| role | VARCHAR(20) | NOT NULL, DEFAULT 'user' | 角色：'admin' 或 'user' |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| last_login_at | DATETIME | NULL | 最后登录时间 |
| is_active | BOOLEAN | DEFAULT TRUE | 账号是否激活 |

**索引：**
- `idx_username`: `username` 唯一索引

**初始化数据：**
```sql
INSERT INTO users (username, password_hash, role) VALUES
('admin', '$2b$12$...', 'admin');  -- 默认密码：123456
```

---

#### 表 2: `albums` - 专辑表

| 字段名 | 类型 | 约束 | 说明 |
| :--- | :--- | :--- | :--- |
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 专辑 ID |
| title | VARCHAR(200) | NOT NULL | 专辑名称 |
| cover_image | VARCHAR(500) | NOT NULL | 封面图路径 |
| description | TEXT | NULL | 专辑简介 |
| sort_order | INTEGER | DEFAULT 0 | 展示排序（越小越靠前） |
| episode_count | INTEGER | DEFAULT 0 | 剧集数量（冗余字段） |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- `idx_sort_order`: `sort_order` 索引（排序优化）

---

#### 表 3: `episodes` - 单集表

| 字段名 | 类型 | 约束 | 说明 |
| :--- | :--- | :--- | :--- |
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 单集 ID |
| album_id | INTEGER | NOT NULL, FOREIGN KEY | 参考专辑表 |
| title | VARCHAR(200) | NOT NULL | 标题（如："第一话"） |
| file_path | VARCHAR(500) | NOT NULL | 服务器存储路径 |
| file_size | INTEGER | DEFAULT 0 | 文件大小（字节） |
| duration | INTEGER | DEFAULT 0 | 时长（秒） |
| sort_order | INTEGER | DEFAULT 0 | 排序权重（越小越靠前） |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 上传时间 |

**索引：**
- `idx_album_id`: `album_id` 索引（查询优化）
- `idx_sort_order`: `sort_order` 索引（排序优化）

**外键约束：**
```sql
FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE CASCADE
```

---

#### 表 4: `sessions` - 会话表（可选，用于审计）

| 字段名 | 类型 | 约束 | 说明 |
| :--- | :--- | :--- | :--- |
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 会话 ID |
| user_id | INTEGER | NOT NULL, FOREIGN KEY | 参考用户表 |
| token | VARCHAR(255) | UNIQUE, NOT NULL | Session Token |
| ip_address | VARCHAR(45) | NULL | 客户端 IP |
| user_agent | VARCHAR(500) | NULL | 客户端 UA |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| expires_at | DATETIME | NOT NULL | 过期时间 |

---

### 2.2 ER 图

```
┌─────────────────┐         ┌─────────────────┐
│     users       │         │     sessions    │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │◄────────│ user_id (FK)    │
│ username        │         │ token           │
│ password_hash   │         │ created_at      │
│ role            │         │ expires_at      │
└─────────────────┘         └─────────────────┘
        ▲
        │ 1:N
        │
┌───────┴─────────┐
│    albums       │
├─────────────────┤
│ id (PK)         │
│ title           │
│ cover_image     │
│ episode_count   │
│ sort_order      │
└───────┬─────────┘
        │ 1:N
        │
┌───────┴─────────┐
│   episodes      │
├─────────────────┤
│ id (PK)         │
│ album_id (FK)   │
│ title           │
│ file_path       │
│ duration        │
│ sort_order      │
└─────────────────┘
```

---

## 3. 核心技术方案

### 3.1 并发控制方案（10人限制）

#### 3.1.1 Redis Key 设计

```
Key:   session:{user_id}
Value: {"token": "xxx", "expires_at": 1704067200}
TTL:   1800 秒（30 分钟）
```

#### 3.1.2 登录校验流程

```python
async def login(username: str, password: str) -> dict:
    # 步骤 1: 查询用户信息
    user = await db.fetch_user_by_username(username)
    if not user or not verify_password(password, user.password_hash):
        raise Unauthorized("用户名或密码错误")

    # 步骤 2: 检查并发限制
    current_sessions = await redis.keys("session:*")
    if len(current_sessions) >= 10:
        raise Forbidden("系统在线人数已达上限（10/10），请稍后重试")

    # 步骤 3: 检查用户是否已在线（同一账号多设备登录限制）
    existing_session = await redis.get(f"session:{user.id}")
    if existing_session:
        await redis.delete(f"session:{user.id}")  # 踢掉旧会话

    # 步骤 4: 生成 Session Token
    token = generate_jwt_token(user_id=user.id, role=user.role)
    session_data = {
        "token": token,
        "expires_at": int(time.time()) + 1800
    }

    # 步骤 5: 写入 Redis，设置 30 分钟过期
    await redis.setex(
        f"session:{user.id}",
        1800,
        json.dumps(session_data)
    )

    # 步骤 6: 更新用户最后登录时间
    await db.update_user_last_login(user.id)

    return {"access_token": token, "user": user}
```

#### 3.1.3 心跳保活机制

**前端：**
```javascript
// 每 15 分钟发送一次心跳请求
setInterval(async () => {
    await fetch('/api/auth/heartbeat', {
        headers: { 'Authorization': `Bearer ${token}` }
    })
}, 15 * 60 * 1000)
```

**后端：**
```python
async def heartbeat(current_user: User):
    # 刷新 Session 过期时间
    await redis.expire(f"session:{current_user.id}", 1800)
    return {"status": "ok", "expires_in": 1800}
```

---

### 3.2 防下载音频流方案

#### 3.2.1 核心原理

**传统模式（不安全）：**
```
用户访问：http://domain.com/static/album1/ep1.mp3
问题：
  1. 可直接右键另存为
  2. IDM 等下载工具可嗅探并下载
  3. 登录后 URL 可分享给他人
```

**本方案（安全）：**
```
用户访问：GET /api/stream/{episode_id}?token=abc123
后端逻辑：
  1. 验证 Token 是否有效
  2. 根据 episode_id 查库获取文件路径 /var/data/album1/ep1.mp3
  3. 使用 Range 请求支持断点续传
  4. 返回 FileResponse，设置 Content-Disposition: inline
  5. URL 中的 Token 与 Session 绑定，失效即断流
```

#### 3.2.2 文件流 API 实现

```python
from fastapi import Depends, HTTPException, Request
from fastapi.responses import FileResponse
import aiofiles

async def stream_audio(
    episode_id: int,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    # 1. 验证用户权限
    if current_user and not current_user.is_active:
        raise HTTPException(403, "账号已被禁用")

    # 2. 查询音频文件路径
    episode = await db.fetch_episode_by_id(episode_id)
    if not episode:
        raise HTTPException(404, "音频不存在")

    # 3. 检查文件是否存在
    if not os.path.exists(episode.file_path):
        raise HTTPException(404, "音频文件丢失")

    # 4. 生成防盗链 Token（额外一层防护）
    stream_token = generate_stream_token(
        user_id=current_user.id,
        episode_id=episode_id,
        expire_seconds=600  # 10 分钟后 Token 失效
    )

    # 5. 验证 Token 参数（防止 URL 分享）
    provided_token = request.query_params.get("token")
    if provided_token != stream_token:
        raise HTTPException(403, "Token 无效或已过期")

    # 6. 返回文件流
    return FileResponse(
        episode.file_path,
        media_type="audio/mpeg",  # 根据实际文件类型设置
        filename=episode.title + ".mp3",
        headers={
            "Content-Disposition": "inline",  # 强制浏览器播放而非下载
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "no-cache, no-store, must-revalidate",
        }
    )
```

#### 3.2.3 Nginx 配置（防直接访问）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态资源
    location / {
        root /app/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # ⚠️ 关键：禁止直接访问音频文件
    location /app/static {
        internal;  # Nginx internal only
        alias /media;
        deny all;
    }
}
```

#### 3.2.4 前端防下载措施

**JavaScript 禁用右键和快捷键：**
```javascript
// 禁用右键菜单
document.addEventListener('contextmenu', (e) => {
    e.preventDefault()
})

// 禁用 F12、Ctrl+S、Ctrl+C
document.addEventListener('keydown', (e) => {
    if (
        e.key === 'F12' ||
        (e.ctrlKey && e.key === 's') ||
        (e.ctrlKey && e.key === 'c') ||
        (e.ctrlKey && e.key === 'u') ||
        (e.ctrlKey && e.key === 'i')
    ) {
        e.preventDefault()
    }
})
```

**APlayer 配置（禁用下载按钮）：**
```javascript
const player = new APlayer({
    container: document.getElementById('player'),
    audio: [...],
    controls: {
        download: false  // 隐藏下载按钮
    }
})
```

---

### 3.3 音频上传方案

#### 3.3.1 前端上传组件

```vue
<template>
  <el-upload
    action="/api/admin/upload/batch"
    :headers="authHeaders"
    multiple
    :limit="20"
    :before-upload="beforeUpload"
    :on-success="handleSuccess"
    :on-error="handleError"
    auto-upload
  >
    <el-button type="primary">选择音频文件</el-button>
  </el-upload>
</template>

<script setup>
// 文件类型和大小校验
const beforeUpload = (file) => {
  const allowedTypes = ['audio/mpeg', 'audio/mp4', 'audio/flac']
  const maxSize = 100 * 1024 * 1024  // 100MB

  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('只支持 MP3、M4A、FLAC 格式')
    return false
  }

  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 100MB')
    return false
  }

  return true
}

const authHeaders = {
  Authorization: `Bearer ${tokenStore.token}`
}
</script>
```

#### 3.3.2 后端上传处理

```python
from fastapi import UploadFile, File, Form
import aiofiles
from mutagen import File as MutagenFile  # 音频元数据解析

async def batch_upload(
    files: list[UploadFile] = File(...),
    album_id: int = Form(...),
    current_user: User = Depends(get_current_admin)
):
    uploaded_episodes = []

    for file in files:
        # 1. 生成文件名（UUID + 原始扩展名）
        filename = f"{uuid.uuid4()}{Path(file.filename).suffix}"
        file_path = f"/media/albums/{album_id}/{filename}"

        # 2. 保存文件
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # 3. 解析音频元数据（时长）
        audio_file = MutagenFile(file_path)
        duration = int(audio_file.info.length) if audio_file else 0

        # 4. 写入数据库
        episode = await db.create_episode(
            album_id=album_id,
            title=file.filename.replace(Path(file.filename).suffix, ''),
            file_path=file_path,
            file_size=len(content),
            duration=duration
        )

        uploaded_episodes.append(episode)

    # 5. 更新专辑的 episode_count
    await db.update_album_episode_count(album_id)

    return {"success": True, "count": len(uploaded_episodes)}
```

---

## 4. API 接口设计

### 4.1 鉴权接口

#### POST /api/auth/login - 登录

**Request Body:**
```json
{
  "username": "admin",
  "password": "123456"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin"
    }
  }
}
```

**Error Response:**
- `401 Unauthorized`: 用户名或密码错误
- `403 Forbidden`: 在线人数已达上限

---

#### POST /api/auth/logout - 登出

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": "已成功登出"
}
```

---

#### POST /api/auth/heartbeat - 心跳保活

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "expires_in": 1800
  }
}
```

---

### 4.2 专辑管理接口（Admin）

#### GET /api/admin/albums - 获取专辑列表

**Query Params:**
- `page`: 页码（默认 1）
- `page_size`: 每页数量（默认 20）

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "total": 25,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": 1,
        "title": "哈利波特与魔法石",
        "cover_image": "/static/covers/1.jpg",
        "description": "J.K.罗琳创作...",
        "episode_count": 10,
        "created_at": "2026-02-28T00:00:00Z"
      }
    ]
  }
}
```

---

#### POST /api/admin/albums - 创建专辑

**Request Body:**
```json
{
  "title": "新专辑",
  "cover_image": "base64_encoded_image",
  "description": "专辑简介",
  "sort_order": 0
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 26,
    "title": "新专辑",
    ...
  }
}
```

---

#### PUT /api/admin/albums/{id} - 更新专辑

**Request Body:** 同创建

**Response (200 OK):** 更新后的专辑信息

---

#### DELETE /api/admin/albums/{id} - 删除专辑

**Response (200 OK):**
```json
{
  "success": true,
  "data": "专辑已删除"
}
```

---

### 4.3 音频管理接口（Admin）

#### POST /api/admin/upload/batch - 批量上传

**Request:** `multipart/form-data`
- `files`: 多个音频文件
- `album_id`: 专辑 ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "count": 5,
    "episodes": [...]
  }
}
```

---

#### GET /api/admin/episodes - 获取专辑剧集（Admin）

**Query Params:**
- `album_id`: 专辑 ID

---

### 4.4 用户收听接口

#### GET /api/albums - 获取专辑列表（用户）

**Response:** 同 Admin 接口，但不包含敏感字段

---

#### GET /api/episodes - 获取专辑剧集

**Query Params:**
- `album_id`: 专辑 ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "album_id": 1,
      "title": "第一话",
      "duration": 1805,
      "sort_order": 1,
      "stream_url": "/api/stream/1?token=abc123"
    }
  ]
}
```

---

#### GET /api/stream/{episode_id} - 获取音频流

**Headers:**
```
Authorization: Bearer {token}
Range: bytes=0-1024  # 可选，断点续传
```

**Response (206 Partial Content 或 200 OK):**
```http
Content-Type: audio/mpeg
Content-Disposition: inline
Content-Length: 1024000
Accept-Ranges: bytes
X-Content-Type-Options: nosniff

{音频流数据}
```

---

## 5. 部署架构

### 5.1 Docker Compose 编排

```yaml
version: '3.8'

services:
  # Redis 缓存服务
  redis:
    image: redis:7-alpine
    container_name: audio-drama-redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - audio-drama-net

  # SQLite 数据持久化
  backend:
    build: ./backend
    container_name: audio-drama-backend
    restart: unless-stopped
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=sqlite:///./data/audio_drama.db
      - SECRET_KEY=your-secret-key-here
      - MAX_CONCURRENT_USERS=10
      - SESSION_EXPIRE_SECONDS=1800
    volumes:
      - db_data:/app/data
      - media_data:/media
    ports:
      - "8000:8000"
    networks:
      - audio-drama-net

  # 前端静态资源服务
  frontend:
    build: ./frontend
    container_name: audio-drama-frontend
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./frontend/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
    networks:
      - audio-drama-net

volumes:
  redis_data:
  db_data:
  media_data:

networks:
  audio-drama-net:
    driver: bridge
```

### 5.2 目录结构

```
audio-drama-system/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI 主应用
│   │   ├── models/           # SQLAlchemy 模型
│   │   ├── schemas/          # Pydantic Schema
│   │   ├── api/              # API 路由
│   │   ├── core/             # 核心配置、工具
│   │   └── db/               # 数据库操作
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # Vue 组件
│   │   ├── views/            # 页面视图
│   │   ├── router/           # 路由配置
│   │   └── stores/           # Pinia 状态管理
│   ├── nginx.conf
│   ├── Dockerfile
│   └── package.json
├── docs/                     # 项目文档
├── deploy/                   # 部署脚本
└── docker-compose.yml
```

---

## 6. 性能优化方案

### 6.1 数据库优化

- 为 `album_id`、`sort_order` 建立索引
- 使用 SQLAlchemy 的 `eager loading` 避免 N+1 查询
- 定期执行 `VACUUM` 优化 SQLite

---

### 6.2 缓存策略

- Redis 缓存专辑列表（TTL: 5 分钟）
- 音频元数据缓存（TTL: 24 小时）

---

### 6.3 前端优化

- 路由懒加载
- 图片懒加载
- 使用 CDN 加速 Element Plus
- Gzip 压缩静态资源

---

## 7. 安全防护

### 7.1 XSS 防御

- 使用 `vue` 的 v-html 前过滤
- Content-Security-Policy（CSP）策略

---

### 7.2 CSRF 防御

- SameSite Cookie 策略
- Token 验证（V1.2）

---

### 7.3 密码安全

- 使用 `bcrypt` 哈希，work factor 12
- 密码强度校验（最小 6 位）

---

## 8. 监控与日志

---

### 8.1 日志记录

- 操作日志（上传、删除、登录）
- 错误日志（Nginx 错误、应用异常）
- 访问日志（Nginx access.log）

---

### 8.2 系统监控

- 在线人数监控（Redis keys）
- 存储空间监控
- API 响应时间（Prometheus + Grafana，V1.2）

---

## 9. 备份与恢复

---

### 9.1 自动备份

```bash
# 每日凌晨 3 点备份数据库
0 3 * * * /app/backup.sh
```

### 9.2 备份脚本

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d)
sqlite3 /app/data/audio_drama.db ".backup /backup/db_$DATE.db"
```

---

## 10. 故障排查

---

| 问题 | 可能原因 | 解决方案 |
| :--- | :--- | :--- |
| 无法登录 | Session 数达上限 | 检查 Redis `keys session:*\` |
| 音频无法播放 | Token 失效 | 刷新页面重新登录 |
| 上传失败 | 磁盘空间不足 | `df -h` 检查存储 |
| API 502 | 后端服务未启动 | `docker ps` 检查容器状态 |

---

## 11. 开发计划

---

| 阶段 | 任务 | 预计工期 |
| :--- | :--- | :--- |
| **阶段一：MVP** | 用户登录、并发控制、专辑管理、音频上传、在线播放 | 5 天 |
| **阶段二：优化** | 剧集排序、播放列表、性能优化 | 3 天 |
| **阶段三：部署** | Docker 编排、Nginx 配置、线上部署 | 2 天 |
| **阶段四：增强** | 系统监控、用户收藏、评论系统 | 5 天 |

---

## 12. 变更记录

---

| 版本 | 日期 | 变更内容 | 作者 |
| :--- | :--- | :--- | :--- |
| V1.0.0 | 2026-02-28 | 初始版本 | AI |
