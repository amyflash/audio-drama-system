# 音频广播剧系统 - 修改记录

## 2026年3月4日 - 部署配置优化

### 背景
项目需要部署到服务器，但服务器有端口限制：只能代理5173端口，后端端口无法代理，只能本地访问。服务器上有docker compose环境。

### 修改内容

#### 1. Docker Compose 配置 (`docker-compose.yml`)
- 将 `image:` 改为 `build:` + `image:` 组合，支持本地构建镜像
  - 后端：`build: {context: ./backend, dockerfile: Dockerfile}`
  - 前端：`build: {context: ./nuxt-frontend, dockerfile: Dockerfile}`
- 后端端口安全限制：`"127.0.0.1:8000:8000"`（仅本地访问）
- 后端环境变量添加：`ALLOW_ORIGINS=*`（支持从环境变量配置CORS）
- 前端环境变量：`API_BASE_URL=http://backend:8000`（容器内通信）

#### 2. 后端跨域配置 (`backend/app/main.py`)
- 修改CORS中间件，从环境变量 `ALLOW_ORIGINS` 读取允许的域名
- 支持逗号分隔的多个域名：`"https://domain1.com,https://domain2.com"`
- 默认值：`["*"]`（允许所有来源，便于快速部署）

#### 3. 前端API配置 (`nuxt-frontend/api/index.ts`)
- 修改 `baseURL = ""`（使用相对路径）
- 所有API请求通过Nuxt服务器代理转发

#### 4. 前端插件配置 (`nuxt-frontend/plugins/api.ts`)
- 修改 `axios.create({ baseURL: '' })`（使用空baseURL）
- 修复 `getStreamUrl` 方法：使用 `/api/stream/${id}`（相对路径）

#### 5. 前端代理配置 (`nuxt-frontend/nuxt.config.ts`)
- 修复代理路径问题：确保 `/api` 前缀正确传递到后端
- 开发环境代理：`'/api/**': { target: 'http://backend:8000/api' }`
- 生产环境路由规则：`'/api/**': { proxy: 'http://backend:8000/api' }`

#### 6. 修复硬编码域名 (`nuxt-frontend/api/episode.ts`)
- 移除硬编码的 `https://h.1006868.xyz`
- 修改为：`${baseURL || ''}/api/stream/${id}`

### 部署架构
```
用户浏览器 → https://q.1006868.xyz/api/*
          ↓ (Nginx/负载均衡器)
     转发到 → http://服务器IP:5173/api/*
          ↓ (Nuxt容器，端口80映射到主机5173)
    代理转发 → http://backend:8000/api/*
          ↓ (后端容器，端口8000仅限本地访问)
    处理并返回响应
```

### 端口映射
| 服务 | 容器端口 | 主机映射 | 外部访问 |
|------|---------|---------|---------|
| 后端 | 8000 | 127.0.0.1:8000 | ❌ 仅本地 |
| 前端 | 80 | 0.0.0.0:5173 | ✅ 公开访问 |

### 快速部署命令
```bash
# 构建镜像
docker-compose build --no-cache

# 启动服务
docker-compose up -d

# 验证部署
curl http://localhost:5173/api/health
curl -X POST http://localhost:5173/api/auth/login -H "Content-Type: application/json"   -d '{"username":"admin","password":"123456"}'
```

### 注意事项
1. 数据卷路径需要根据服务器实际情况调整（当前使用 `/home/gbj/` 相关路径）
2. 生产环境建议通过环境变量设置 `ALLOW_ORIGINS` 指定允许的域名
3. 前端容器通过 `backend` 服务名访问后端，无需使用IP地址
4. 所有API请求通过Nuxt服务器代理，符合"只能代理5173端口"的限制

### 问题修复记录
- **问题**：前端访问登录接口时，后台收到 `/auth/login` 返回404
- **原因**：Nuxt代理默认剥离了 `/api` 前缀
- **解决方案**：在代理目标URL中显式包含 `/api` 前缀

## 2026年3月5日 - 配置参数外部化

### 背景
将上传文件大小限制和同时在线人数限制从代码硬编码提取到外部配置，方便部署时灵活调整。

### 修改内容

#### 1. 后端配置类 (`backend/app/core/config.py`)
- 已定义 `UPLOAD_MAX_FILE_SIZE` 和 `MAX_CONCURRENT_USERS` 配置项
- 使用 Pydantic Settings 支持环境变量自动加载

#### 2. 上传文件大小限制外部化
- **`backend/app/api/albums.py`**: 将 `MAX_FILE_SIZE = 104857600` 改为 `MAX_FILE_SIZE = settings.UPLOAD_MAX_FILE_SIZE`
- **`backend/app/api/episodes.py`**: 将 `MAX_FILE_SIZE = 104857600` 改为 `MAX_FILE_SIZE = settings.UPLOAD_MAX_FILE_SIZE`
- **`backend/app/api/upload.py`**: 将 `MAX_FILE_SIZE = 104857600` 改为 `MAX_FILE_SIZE = settings.UPLOAD_MAX_FILE_SIZE`
- 添加了 `from app.core.config import settings` 导入

#### 3. Docker Compose 环境变量配置 (`docker-compose.yml`)
- 添加环境变量支持 `${VAR_NAME:-default}` 语法
- 关键配置项：
  - `MAX_CONCURRENT_USERS=${MAX_CONCURRENT_USERS:-10}`
  - `UPLOAD_MAX_FILE_SIZE=${UPLOAD_MAX_FILE_SIZE:-104857600}`
- 支持通过项目根目录 `.env` 文件覆盖所有配置

#### 4. 环境变量示例文件 (`backend/.env.example`)
- 包含所有可配置参数，包括：
  - `MAX_CONCURRENT_USERS=10`
  - `UPLOAD_MAX_FILE_SIZE=104857600`
  - `SESSION_EXPIRE_SECONDS=1800`
  - `STREAM_TOKEN_EXPIRE_SECONDS=600`

### 配置方式

#### 方式一：直接修改 docker-compose.yml
```yaml
environment:
  - MAX_CONCURRENT_USERS=20
  - UPLOAD_MAX_FILE_SIZE=209715200  # 200MB
```

#### 方式二：通过 .env 文件覆盖（推荐）
1. 复制环境变量模板：`cp backend/.env.example .env`
2. 编辑 `.env` 文件修改参数
3. 启动服务：`docker-compose up -d`

#### 方式三：部署时通过命令行传递
```bash
MAX_CONCURRENT_USERS=20 UPLOAD_MAX_FILE_SIZE=209715200 docker-compose up -d
```

### 配置优先级
1. `docker-compose.yml` 中直接设置的值（最高）
2. `.env` 文件中的值（次高）
3. `config.py` 中的默认值（最低）

### 验证测试
- 通过 Python 语法检查确保所有修改文件无语法错误
- 配置系统使用 Pydantic Settings，支持环境变量自动加载和类型验证

### 参数说明
| 参数名 | 默认值 | 说明 |
|--------|--------|------|
| `MAX_CONCURRENT_USERS` | 10 | 最大同时在线用户数 |
| `UPLOAD_MAX_FILE_SIZE` | 104857600 (100MB) | 单个音频文件上传大小限制（字节） |
| `SESSION_EXPIRE_SECONDS` | 1800 | 用户会话过期时间（秒） |
| `STREAM_TOKEN_EXPIRE_SECONDS` | 600 | 流媒体播放令牌过期时间（秒） |

### 注意事项
1. 所有配置项已完全外部化，无需修改代码即可调整系统行为
2. 生产环境务必修改 `SECRET_KEY` 和 `JWT_SECRET_KEY`
3. 上传文件大小限制以字节为单位，计算方式：`1MB = 1048576 字节`
4. 同时在线人数限制基于会话管理，超限时新用户无法登录

### nginx端也要修改允许的上传文件大小
server {
    listen 443 ssl ; 
    server_name gbj.516768.xyz; 
    # 新增：设置整个域名允许的最大上传文件大小为200M
    client_max_body_size 200M;
    
    index index.php index.html index.htm default.php default.htm default.html;
~~~