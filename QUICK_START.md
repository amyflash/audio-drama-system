# 🚀 前后端分离快速开始指南

## 📊 一句话总结

**开发环境:** Nuxt代理所有API请求 → 无跨域  
**生产环境:** 后端同时serves前端 → 无跨域  

都避免了浏览器的CORS问题！✨

---

## ⚡ 5分钟快速开始

### Step 1: 配置环境变量

#### 后端 (`backend/.env`)
```bash
ENV=development
ALLOW_ORIGINS=  # 留空，自动配置
API_BASE_URL=http://localhost:8001
```

#### 前端 (`nuxt-frontend/.env`)
```bash
API_BASE_URL=http://localhost:8001
NODE_ENV=development
```

### Step 2: 启动服务

#### 方式A: 同时启动 (推荐)
```bash
# 一个终端启动前端
cd nuxt-frontend
npm run dev

# 另一个终端启动后端
cd backend
python -m uvicorn app.main:app --reload
```

#### 方式B: 使用启动脚本
```bash
chmod +x start-all.sh
./start-all.sh
```

### Step 3: 验证

```bash
# 在浏览器访问
http://localhost:5173

# 应该能看到:
# ✅ 页面加载（前端SPA）
# ✅ 登录功能正常（API请求成功）
# ✅ DevTools Network中无CORS错误
```

---

## 🔍 工作原理图解

### 开发环境请求流程

```
┌─────────────────────────────────────────────────────────┐
│ 浏览器 (localhost:5173)                                 │
│  页面: http://localhost:5173/albums                     │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ axios.get('/api/admin/albums')
                   │ 请求URL: http://localhost:5173/api/admin/albums
                   ▼
┌─────────────────────────────────────────────────────────┐
│ Nuxt Dev服务器 (localhost:5173)                        │
│ 看到 /api/** 路径                                       │
│ 触发 devProxy 规则                                      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ 代理转发 (服务器→服务器，非浏览器)
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ FastAPI后端 (localhost:8001)                           │
│ 处理请求: /api/admin/albums                            │
│ 返回JSON数据                                            │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ 返回响应
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ Nuxt Dev服务器                                         │
│ 返回结果给浏览器                                        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 浏览器                                                  │
│ 收到数据，更新UI                                       │
│ 从浏览器角度：只请求了localhost:5173！                │
│ 无跨域问题 ✅                                          │
└─────────────────────────────────────────────────────────┘
```

**关键:** 代理发生在**服务器之间**，不是浏览器！

### 生产环境请求流程

```
┌─────────────────────────────────────────────────────────┐
│ 浏览器 (https://yourdomain.com)                        │
│ 页面: https://yourdomain.com/albums                    │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ axios.get('/api/admin/albums')
                   │ 请求URL: https://yourdomain.com/api/admin/albums
                   │ (同一域名！)
                   ▼
┌─────────────────────────────────────────────────────────┐
│ FastAPI后端 (yourdomain.com)                           │
│ ├─ /api/...      → 处理API请求                        │
│ ├─ /            → 服务前端静态文件                     │
│ └─ /docs        → Swagger文档                          │
│                                                         │
│ 无需CORS！都是同一域名 ✅                             │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 浏览器                                                  │
│ 收到数据，更新UI                                       │
│ 零跨域问题 ✅                                         │
└─────────────────────────────────────────────────────────┘
```

**关键:** 前端和后端在同一域名，浏览器压根不会触发跨域！

---

## 🛠️ 常见任务

### 任务1: 添加新API端点

#### 1. 后端添加路由 (`backend/app/api/xxx.py`)
```python
from fastapi import APIRouter

router = APIRouter(tags=["xxx"])

@router.get("/xxx")
async def get_xxx():
    return {"data": "xxx"}
```

#### 2. 主应用注册 (`backend/app/main.py`)
```python
from app.api import xxx
app.include_router(xxx.router, prefix="/api")
```

#### 3. 前端调用 (`nuxt-frontend/api/xxx.ts`)
```typescript
import api from './index'

export const getXxx = () => {
  return api.get('/api/xxx')
}
```

#### 4. 前端使用
```typescript
const { data } = await getXxx()
```

**无需修改任何CORS配置！** 前端会自动代理到后端。

### 任务2: 部署到生产

#### Step 1: 构建前端
```bash
cd nuxt-frontend
npm run build

# 这会生成 .output 目录
```

#### Step 2: 复制前端到后端
```bash
# 使用脚本 (推荐)
./build-frontend.sh

# 或手动复制
cp -r nuxt-frontend/.output/public/* backend/static/
```

#### Step 3: 启动后端
```bash
cd backend
# 生产启动 (无reload)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

#### Step 4: 验证
```bash
curl https://yourdomain.com/  # 返回HTML
curl https://yourdomain.com/api/health  # 返回JSON
curl https://yourdomain.com/albums/1  # SPA路由 - 返回HTML
```

---

## 🔐 环境变量设置详解

### 关键变量说明

#### `ENV` (运行环境)
```bash
ENV=development   # 开发 - 自动配置CORS允许localhost:5173
ENV=testing       # 测试 - 允许指定的测试域名
ENV=production    # 生产 - 禁用CORS（同域部署）
```

#### `ALLOW_ORIGINS` (CORS白名单)
```bash
# 策略1: 留空 (推荐! 自动根据ENV配置)
ALLOW_ORIGINS=

# 策略2: 指定单个域名
ALLOW_ORIGINS=https://yourdomain.com

# 策略3: 指定多个域名 (多前端应用)
ALLOW_ORIGINS=https://app.com,https://admin.app.com

# 策略4: 本地+远程 (过渡期)
ALLOW_ORIGINS=http://localhost:5173,https://yourdomain.com
```

#### `API_BASE_URL` (Nuxt后端地址)
```bash
# 开发环境 - 指定后端地址
API_BASE_URL=http://localhost:8001

# 生产环境 - 留空 (使用相对路径)
API_BASE_URL=
```

### 配置矩阵

| 环境 | ENV | ALLOW_ORIGINS | API_BASE_URL | 说明 |
|------|-----|---------------|--------------|------|
| 本地开发 | development | (留空) | http://localhost:8001 | 自动配置localhost |
| CI/CD测试 | testing | https://ci.example.com | https://api.ci.example.com | 指定测试域名 |
| 生产部署 | production | (留空) | (留空) | 同域，无需CORS |
| 多前端 | production | https://a.com,https://b.com | (留空) | 支持多个应用 |

---

## 🐛 常见问题排查

### 问题1: 浏览器console出现CORS错误

```
Access to XMLHttpRequest at 'http://localhost:8001/api/...' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**原因分析:**
- ❌ 前端直接请求后端，没有通过Nuxt代理

**检查清单:**
```bash
# 1. Nuxt devProxy是否启动?
# → 看 npm run dev 的输出，应该显示 "Listening on http://localhost:5173"

# 2. 请求是否真的通过代理?
# → DevTools → Network → 看请求URL
#   应该是: http://localhost:5173/api/...
#   不应该是: http://localhost:8001/api/...

# 3. API_BASE_URL是否配置正确?
echo $API_BASE_URL

# 4. nuxt.config.ts中devProxy是否配置?
grep -A5 "devProxy" nuxt.config.ts
```

**解决方案:**
```bash
# 重启Nuxt
npm run dev

# 清除浏览器缓存
# DevTools → Application → Storage → Clear All
```

### 问题2: 生产环境API返回404

```
GET https://yourdomain.com/api/albums 404 Not Found
```

**原因分析:**
- ❌ 前端静态文件未正确部署到后端

**检查清单:**
```bash
# 1. 静态文件是否存在?
ls backend/static/index.html  # 应该存在

# 2. 是否使用了最新的构建?
./build-frontend.sh  # 重新构建并复制

# 3. 后端是否正确serving SPA?
# 访问 https://yourdomain.com/ 应该返回HTML
curl -I https://yourdomain.com/
```

**解决方案:**
```bash
# 重新构建
cd nuxt-frontend
npm run build

# 复制到后端
cp -r .output/public/* ../backend/static/

# 重启后端
cd ../backend
python -m uvicorn app.main:app --reload
```

### 问题3: 登录成功但后续请求返回401

```
POST /api/auth/login 200 OK （登录成功）
GET /api/admin/albums 401 Unauthorized （后续请求失败）
```

**原因分析:**
- ❌ Authorization header没有被正确发送

**检查清单:**
```typescript
// api/index.ts 中应该有:
const api = axios.create({
  withCredentials: true  // ✅ 这一行必须有
})

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`  // ✅ 这一行必须有
    }
  }
  return config
})
```

**调试步骤:**
```bash
# 1. 检查localStorage中是否保存了token
# DevTools → Application → Storage → localStorage
# 应该看到 "token" 键

# 2. 检查Network中的Authorization header
# DevTools → Network → 任意API请求 → Headers
# 应该看到: Authorization: Bearer <token>

# 3. 检查服务器日志
# 后端应该打印: "Authorization: Bearer <token>"
```

**解决方案:**
```typescript
// 确保拦截器正确添加token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

### 问题4: 刷新页面后返回404

```
访问 http://localhost:5173/albums/123 → 正常
刷新浏览器 → 404 Not Found
```

**原因分析:**
- ❌ SPA路由fallback配置不正确

**检查清单:**
```bash
# Nuxt的 ssr: false 是否设置?
grep "ssr:" nuxt.config.ts

# 后端的SPAMiddleware是否启用?
grep -A20 "SPAMiddleware" backend/app/main.py
```

**解决方案:**

前端检查 (`nuxt.config.ts`):
```typescript
export default defineNuxtConfig({
  ssr: false,  // ✅ 必须禁用SSR
  // ...
})
```

后端检查 (`backend/app/main.py`):
```python
class SPAMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # ... 跳过API和静态资源后，返回index.html
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
```

---

## 📝 最佳实践清单

- [ ] 前端API调用使用**相对路径** (如 `/api/...`)
- [ ] `ALLOW_ORIGINS` 在生产环境**留空** (或明确指定)
- [ ] `API_BASE_URL` 在生产环境**留空** (使用相对路径)
- [ ] Axios配置 `withCredentials: true` (支持跨域时发送cookies)
- [ ] 所有API请求通过**统一的axios实例** (便于全局配置)
- [ ] 使用**拦截器处理token** (自动添加Authorization header)
- [ ] 生产环境使用**同域部署** (一个域名运行前后端)
- [ ] 定期检查**浏览器DevTools** (确认无CORS错误)

---

## 📚 参考资源

### 配置文件
- `backend/.env.example` - 后端配置说明
- `nuxt-frontend/.env.example` - 前端配置说明
- `CORS_AND_ROUTING.md` - 详细解决方案文档

### 相关概念
- [Nuxt DevProxy文档](https://nuxt.com/docs/guide/concepts/server-engine#route-rules)
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [Axios拦截器](https://axios-http.com/docs/interceptors)
- [SPA路由与服务器](https://developer.mozilla.org/en-US/docs/Glossary/SPA)

---

## 💡 总结

| 场景 | 方案 | 好处 |
|------|------|------|
| **本地开发** | Nuxt代理 + CORS允许localhost | 零跨域，热更新快速 |
| **生产部署** | 同域部署 (后端serving前端) | 最安全，最简单，最快 |
| **多前端** | 显式CORS配置 | 支持独立部署多个应用 |

无论哪种场景，都完全**避免了浏览器CORS问题**！✨
