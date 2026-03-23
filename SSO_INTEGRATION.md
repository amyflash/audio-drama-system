# JWT-Auth SSO 集成完全指南

## 📊 当前SSO集成状态分析

### 已有的SSO实现

你的项目已经集成了 `sso_client`：

```python
# backend/app/main.py
from sso_client import create_sso_router

sso = create_sso_router(
    secret_key=settings.SSO_SECRET_KEY,
    jwt_auth_url=settings.SSO_JWT_AUTH_URL,
    jwt_expire_seconds=settings.JWT_EXPIRE_SECONDS,
    algorithm=settings.SSO_ALGORITHM,
    sso_enabled=settings.SSO_ENABLED,
)

# 注册SSO路由
app.include_router(sso.router, prefix="/api")
```

### SSO关键配置

```python
# backend/app/core/config.py
SSO_ENABLED: bool = True
SSO_JWT_AUTH_URL: str = "http://localhost:8000"  # jwt-auth 服务地址
SSO_SECRET_KEY: str = "..."  # 与 jwt-auth 的 SECRET_KEY 一致
SSO_ALGORITHM: str = "HS256"
```

### SSO已被集成到的路由

```python
# 需要认证的路由
from sso_client import require_admin, get_current_user

@router.post("/albums")
async def create_album(
    item: AlbumCreate,
    current_user: UserInfo = Depends(require_admin)  # ✅ SSO认证
):
    # ...
```

---

## ✅ 好消息：我们的调整完全兼容SSO！

### 为什么兼容？

#### 1. **CORS配置对SSO友好**

```python
# ✅ 新的三层策略
def get_cors_config():
    # 开发环境: 自动允许 http://localhost:5173
    # 生产环境: 禁用CORS (同域)
```

**对SSO的影响:**
- 开发: 前端 (5173) 可以调用后端 (8001) 的 `/api/auth/login` SSO路由
- 生产: 同域部署，无需CORS

#### 2. **前端API客户端对SSO友好**

```typescript
// ✅ nuxt-frontend/api/index.ts
const api = axios.create({
  withCredentials: true  // ✅ 支持跨域时发送cookies
})

// ✅ 自动添加Authorization header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`  // ✅ SSO token
  }
  return config
})
```

#### 3. **路由策略对SSO友好**

```typescript
// ✅ nuxt-frontend/nuxt.config.ts
nitro: {
  devProxy: {
    '/api/**': {
      target: 'http://localhost:8001',  // ✅ 包括SSO路由
      changeOrigin: true
    }
  }
}
```

所有 `/api/**` 请求都代理到后端，包括：
- `/api/auth/login` (SSO登录)
- `/api/auth/logout` (SSO登出)
- `/api/admin/albums` (需认证的API)

---

## 🎯 最优的SSO+跨域方案

### 开发环境架构

```
┌─────────────────────────────────────────────────────┐
│ 浏览器 (localhost:5173)                             │
│ ┌─ 前端应用 (Nuxt SPA)                             │
│ └─ localStorage: token (SSO JWT)                   │
└─────────────────────────────────────────────────────┘
                      │
         (所有/api/** 通过代理)
                      │
┌─────────────────────────────────────────────────────┐
│ Nuxt Dev服务器 (localhost:5173)                    │
│ devProxy 中间件                                     │
│ ├─ /api/auth/** → jwt-auth (8000)                 │
│ ├─ /api/admin/** → 自己的API (8001)               │
│ └─ /api/stream/** → 流媒体API (8001)              │
└─────────────────────────────────────────────────────┘
         ↓           ↓           ↓
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │jwt-auth │  │FastAPI  │  │FastAPI  │
    │  8000   │  │  8001   │  │  8001   │
    └─────────┘  └─────────┘  └─────────┘
```

**核心要点:**
- 浏览器只请求 Nuxt (5173)
- 所有后端通信通过代理
- 无需SSO处的CORS配置 ✅
- Token自动添加到所有请求 ✅

### 生产环境架构

```
┌─────────────────────────────────────────────────────┐
│ 浏览器 (yourdomain.com)                             │
│ ├─ 前端应用 (从后端加载)                           │
│ └─ localStorage: token (SSO JWT)                   │
└─────────────────────────────────────────────────────┘
                      │
          (同域请求，无需CORS)
                      │
┌─────────────────────────────────────────────────────┐
│ FastAPI (yourdomain.com)                           │
│ ├─ GET /           → serve 前端SPA                 │
│ ├─ GET /api/auth/login   → 验证(jwt-auth)        │
│ ├─ POST /api/admin/**    → 业务API                │
│ └─ GET /api/stream/**    → 流媒体API              │
│                                                     │
│ CORS中间件: 禁用 (同域无需CORS) ✅               │
└─────────────────────────────────────────────────────┘
         │
         │ (内部调用)
         ▼
┌─────────────────────────────────────────────────────┐
│ jwt-auth (localhost:8000)                          │
│ ├─ POST /auth/login   → 验证用户                   │
│ ├─ POST /auth/logout  → 清除token                 │
│ └─ GET /auth/user     → 获取用户信息              │
└─────────────────────────────────────────────────────┘
```

**核心优势:**
- 完全同域，零跨域问题
- 后端内部调用jwt-auth，无CORS需求
- 生产部署最简单最安全 ✅

---

## 🔧 SSO集成具体配置

### Step 1: 配置环境变量

**backend/.env**
```bash
# 环境
ENV=development

# SSO配置
SSO_ENABLED=true
SSO_JWT_AUTH_URL=http://localhost:8000         # jwt-auth地址
SSO_SECRET_KEY=你的共享密钥                     # 与jwt-auth一致！
SSO_ALGORITHM=HS256

# CORS配置 (推荐留空，自动配置)
ALLOW_ORIGINS=

# jwt-auth服务的内部调用地址 (可选)
JWT_AUTH_INTERNAL_URL=http://localhost:8000    # 同上，或内网地址
```

### Step 2: Nuxt前端配置

**nuxt-frontend/.env**
```bash
# 后端地址
API_BASE_URL=http://localhost:8001

# 可选: jwt-auth直接地址 (仅开发)
# SSO_AUTH_URL=http://localhost:8000

NODE_ENV=development
```

### Step 3: 前端SSO登录实现

```typescript
// nuxt-frontend/api/auth.ts
import api from './index'

export const loginWithSSO = async (username: string, password: string) => {
  // 调用后端SSO路由，它会转发到jwt-auth
  const response = await api.post('/api/auth/login', {
    username,
    password
  })
  
  // 保存token到localStorage
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token)
  }
  
  return response.data
}

export const logout = async () => {
  await api.post('/api/auth/logout')
  localStorage.removeItem('token')
}

export const getCurrentUser = async () => {
  return api.get('/api/auth/user')
}
```

### Step 4: 后端SSO路由已自动注册

```python
# ✅ backend/app/main.py 已自动包含:
app.include_router(sso.router, prefix="/api")

# 这提供了以下路由:
# POST /api/auth/login     - SSO登录
# POST /api/auth/logout    - SSO登出
# GET /api/auth/user       - 获取当前用户
# POST /api/auth/refresh   - 刷新token (可选)
```

### Step 5: 受保护的路由自动使用SSO

```python
# ✅ backend/app/api/albums.py
from sso_client import require_admin, get_current_user

@router.post("/albums")
async def create_album(
    item: AlbumCreate,
    current_user: UserInfo = Depends(require_admin)  # ✅ 自动验证SSO token
):
    # current_user 包含: user_id, username, roles等
    # ...
```

---

## 🚀 完整工作流

### 开发环境工作流

```
1. 用户在浏览器访问 http://localhost:5173
   ↓
2. 点击登录，输入用户名密码
   ↓
3. 前端调用 api.post('/api/auth/login')
   ↓
4. Nuxt devProxy 代理到 http://localhost:8001/api/auth/login
   ↓
5. FastAPI后端接收，调用 sso_client
   ↓
6. sso_client 转发到 jwt-auth (http://localhost:8000)
   ↓
7. jwt-auth 验证用户，返回JWT token
   ↓
8. FastAPI返回token给前端
   ↓
9. 前端保存token到localStorage
   ↓
10. 后续所有请求自动添加: Authorization: Bearer <token>
    ↓
11. 后端自动验证token (通过 require_admin 等)
    ↓
12. 请求成功处理！✅
```

### 生产环境工作流

```
1. 用户在浏览器访问 https://yourdomain.com
   ↓
2. FastAPI serve前端 (GET /)
   ↓
3. 点击登录，调用 api.post('/api/auth/login')
   ↓
4. 请求到 https://yourdomain.com/api/auth/login (同域！)
   ↓
5. FastAPI后端接收，调用 sso_client
   ↓
6. sso_client 转发到 jwt-auth (内部: http://localhost:8000)
   ↓
7. jwt-auth 验证用户，返回JWT token
   ↓
8. FastAPI返回token (无需CORS! ✅)
   ↓
9-12. 后续流程同上
```

---

## 🔐 安全最佳实践

### 1. 密钥管理

**critical: SSO_SECRET_KEY 必须与 jwt-auth 一致！**

```bash
# ✅ 正确做法
backend/.env:
  SSO_SECRET_KEY=abc123xyz  # 与jwt-auth的SECRET_KEY相同

# ❌ 错误做法
backend/.env:
  SSO_SECRET_KEY=不同的密钥  # 会导致token验证失败
```

**怎样获取jwt-auth的密钥:**
```bash
# 查看jwt-auth服务
cat shared/sso_client/.env
# 获取 SECRET_KEY 值，复制到 backend/.env
```

### 2. 环境变量安全

```bash
# ✅ 开发环境 (可以明文)
backend/.env (gitignore)
  ENV=development
  SSO_SECRET_KEY=...

# ✅ 生产环境 (通过环境变量注入)
docker run -e SSO_SECRET_KEY="..." ...

# ❌ 避免
不要在git中提交 SSO_SECRET_KEY
```

### 3. CORS与SSO安全

```python
# ✅ 开发环境: 仅允许localhost
ENV=development
ALLOW_ORIGINS=  # 自动配置localhost:5173

# ✅ 生产环境: 禁用CORS (同域)
ENV=production
ALLOW_ORIGINS=  # 留空，禁用CORS

# ❌ 危险: 不要使用
ALLOW_ORIGINS=*  # 任何来源都能调用SSO!
```

### 4. Token存储安全

```typescript
// ✅ 前端token存储
localStorage.setItem('token', sso_token)  // 简单但易被XSS攻击

// 更安全的方式 (可选):
// 1. 将token存在HttpOnly Cookie
// 2. 使用sessionStorage而非localStorage
// 3. 实现token刷新机制
```

---

## 🧪 SSO集成测试清单

### 开发环境测试

```bash
# 1. 启动jwt-auth (端口8000)
cd shared/sso_client
python -m uvicorn app.main:app --port 8000

# 2. 启动音频剧后端 (端口8001)
cd backend
python -m uvicorn app.main:app --port 8001

# 3. 启动前端 (端口5173)
cd nuxt-frontend
npm run dev

# 4. 测试SSO工作流
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'

# 5. 验证返回token
# 应该返回: {"access_token":"...", "token_type":"bearer"}

# 6. 使用token调用受保护API
curl -X GET http://localhost:8001/api/admin/albums \
  -H "Authorization: Bearer <token>"

# 应该返回: {"success":true, "data":[...]}
```

### 生产环境测试

```bash
# 1. 构建前端
./build-frontend.sh

# 2. 启动后端 (供应jwt-auth地址)
SSO_JWT_AUTH_URL=http://internal-jwt-auth:8000 \
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# 3. 访问应用
curl https://yourdomain.com/api/auth/login

# 应该有CORS headers (但实际上不需要，因为同域)
```

---

## 🔀 多前端应用的SSO集成

如果你想支持多个前端应用都使用同一个jwt-auth：

### 架构

```
┌─────────────┐  ┌─────────────┐
│ App 1       │  │ App 2       │  ← 多个前端
│ (app1.com)  │  │ (app2.com)  │
└──────┬──────┘  └──────┬──────┘
       │                 │
       └────────┬────────┘
                │
          (都请求)
                │
         ┌──────▼──────┐
         │jwt-auth     │
         │(8000)       │  ← 统一SSO
         └─────────────┘
```

### 配置

```bash
# jwt-auth (shared/sso_client/.env)
ALLOW_ORIGINS=https://app1.com,https://app2.com

# backend1 (.env)
SSO_JWT_AUTH_URL=http://jwt-auth:8000
SSO_SECRET_KEY=...

# backend2 (.env)
SSO_JWT_AUTH_URL=http://jwt-auth:8000
SSO_SECRET_KEY=...  # 同一个!
```

---

## ❓ 常见SSO问题排查

### Q1: Token验证失败 (401)

**原因:** SSO_SECRET_KEY 不匹配

```bash
# 检查
echo $SSO_SECRET_KEY  # backend .env
cat shared/sso_client/.env  # jwt-auth

# 应该相同！如果不同，复制jwt-auth的值到backend
```

### Q2: 无法连接到jwt-auth

**原因:** SSO_JWT_AUTH_URL 不正确

```bash
# 开发环境
SSO_JWT_AUTH_URL=http://localhost:8000  # 本地端口
curl http://localhost:8000/health  # 验证jwt-auth在运行

# 生产环境
SSO_JWT_AUTH_URL=http://jwt-auth:8000  # Docker内网地址
# 或
SSO_JWT_AUTH_URL=http://internal-dns.example.com  # 内网DNS
```

### Q3: 前端收到CORS错误

**原因:** CORS配置不正确

```bash
# ✅ 正确做法
ENV=development
ALLOW_ORIGINS=  # 留空，自动配置

# ❌ 错误做法
ALLOW_ORIGINS=""  # 空字符串会导致匹配失败!
```

### Q4: SSO路由不可用 (404)

**原因:** sso_router 未注册

```python
# ✅ backend/app/main.py 应该有:
from sso_client import create_sso_router
app.include_router(sso.router, prefix="/api")

# 验证:
curl http://localhost:8001/api/auth/login
# 应该返回: {"detail": "Method Not Allowed"}
# 而不是: {"detail": "Not Found"}
```

---

## 📈 从我们的优化中获益

### 1. 开发效率提升

```
之前: 
  - 需要同时启动前端、后端、jwt-auth
  - 处理复杂的CORS配置
  - 调试跨域问题困难

之后: ✅
  - 前端自动代理所有请求
  - CORS自动配置
  - 开发体验最优化
```

### 2. 生产部署简化

```
之前:
  - 需要分别配置前端、后端、SSO的CORS
  - 部署多个服务
  - 跨服务通信复杂

之后: ✅
  - 同域部署，零CORS配置
  - 一个后端服务(内部调用jwt-auth)
  - 部署流程最简
```

### 3. 安全性提升

```
之前:
  - allow_origins=["*"] 危险
  - Token容易在CORS中暴露

之后: ✅
  - 生产环境禁用CORS
  - Token安全传输
  - 生产安全性最高
```

---

## 🎯 推荐的SSO部署方式

### 开发环境 (最简单)

```bash
# 终端1
cd shared/sso_client && python -m uvicorn app.main:app --port 8000

# 终端2  
cd backend && python -m uvicorn app.main:app --port 8001

# 终端3
cd nuxt-frontend && npm run dev
```

环境变量自动配置，无需修改 ✅

### 生产环境 (最优雅)

```dockerfile
# Dockerfile
FROM python:3.11

# 部署前端
COPY nuxt-frontend/.output/public /app/static

# 部署后端
COPY backend /app/backend
RUN pip install -r requirements.txt

# 启动后端 (同时serve前端SPA和API)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

环境变量通过 `-e` 注入：
```bash
docker run -e SSO_JWT_AUTH_URL=http://jwt-auth:8000 \
           -e SSO_SECRET_KEY=... \
           audio-drama-system:latest
```

---

## ✅ SSO集成完整清单

- [ ] 获取jwt-auth的 SECRET_KEY
- [ ] 更新backend/.env中的SSO_SECRET_KEY
- [ ] 验证SSO_JWT_AUTH_URL正确
- [ ] 启动jwt-auth服务 (端口8000)
- [ ] 启动后端服务 (端口8001)
- [ ] 启动前端服务 (端口5173)
- [ ] 测试登录流程
- [ ] 测试受保护路由需要token
- [ ] 测试token过期处理
- [ ] 验证生产环境同域部署
- [ ] 配置生产环境环境变量
- [ ] 测试生产SSO流程

---

## 💡 总结

### 我们的调整对SSO非常友好！

| 方面 | 如何帮助SSO | 结果 |
|------|-----------|------|
| **CORS配置** | 智能自动配置，开发自动允许5173，生产禁用 | ✅ SSO无CORS问题 |
| **代理模式** | 前端所有请求通过代理，包括SSO | ✅ 浏览器无跨域 |
| **API客户端** | 自动添加Authorization header | ✅ Token自动传递 |
| **路由注册** | `/api/**` 包含SSO路由 | ✅ SSO路由可用 |
| **同域部署** | 生产后端serve前端 | ✅ SSO最安全 |

### 最大的优势

```
开发: 无需处理CORS，专注SSO逻辑
生产: 同域部署，SSO最安全可靠
迁移: 代码无需修改，自动适应环境
```

---

**结论:** 🎉 我们的优化完全支持SSO，甚至让SSO集成更加优雅！
