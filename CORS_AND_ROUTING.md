# 🎯 前后端分离：跨域与路由完全解决方案

## 📖 项目当前架构

```
┌─────────────────────────────────────┐
│   用户浏览器                         │
└────────────┬────────────────────────┘
             │
    ┌────────▼────────┐
    │  开发环境        │   生产环境
    │ (localhost)     │  (同一域名)
    └────────┬────────┘
             │
    ┌────────▼─────────────┐
    │  Nuxt应用            │
    │  ├─ /api/** 代理      │
    │  └─ 前端路由         │
    └────────┬─────────────┘
             │
    ┌────────▼──────────────┐
    │ FastAPI后端           │
    │ ├─ /api/* 路由        │
    │ ├─ CORS配置           │
    │ └─ /static SPA        │
    └───────────────────────┘
```

---

## 🔧 当前方案如何工作

### 开发环境 (Development)

**无跨域问题!** ✨

```
浏览器请求: http://localhost:5173/api/albums
           ↓
           Nuxt代理服务器 (localhost:5173)
           ↓ (转发)
后端处理: http://localhost:8001/api/albums
           ↓
返回结果 → 浏览器
```

**关键点:**
- 浏览器只看到 `localhost:5173`
- 跨域发生在**服务器之间**，不是浏览器！
- **不需要CORS配置就能工作**

### 生产环境 (Production)

**零跨域问题!** ✨

```
浏览器请求: https://yourdomain.com/api/albums
           ↓
后端FastAPI (serving)
  ├─ /api/albums → API逻辑
  └─ / → 前端静态文件 (SPA)
           ↓
返回结果 → 浏览器
```

**关键点:**
- 完全同域，浏览器不发起跨域请求
- 后端同时serves API和前端
- CORS中间件可完全禁用

---

## ⚙️ 环境变量配置

### 开发环境

```bash
# .env.development (Nuxt前端)
API_BASE_URL=http://localhost:8001
NODE_ENV=development

# .env (FastAPI后端)
ENV=development
ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 生产环境

```bash
# .env.production (Nuxt前端)
API_BASE_URL=  # 留空！使用相对路径
NODE_ENV=production

# .env (FastAPI后端)
ENV=production
ALLOW_ORIGINS=  # 留空！生产环境同域，无需CORS
```

---

## 📋 CORS配置解释

### 之前 (✗ 不安全)
```python
allow_origins = ["*"]  # 任何来源都可访问！
```

### 现在 (✓ 智能配置)
```python
def get_cors_config():
    env = os.getenv("ENV", "development")
    origins_str = os.getenv("ALLOW_ORIGINS", "")
    
    # 1. 明确指定 (推荐生产)
    if origins_str:
        return origins_str.split(",")
    
    # 2. 开发环境 (仅本地前端)
    if env == "development":
        return ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # 3. 生产环境 (同域，无需CORS)
    return []
```

**三层策略:**

| 优先级 | 场景 | 配置 | 说明 |
|--------|------|------|------|
| 1️⃣ | 明确指定 | `ALLOW_ORIGINS=https://a.com,https://b.com` | 最优先，支持多前端 |
| 2️⃣ | 开发环境 | `ENV=development` | 自动配置本地端口 |
| 3️⃣ | 生产环境 | `ENV=production` + 无ALLOW_ORIGINS | 同域部署，禁用CORS |

---

## 🚀 路由配置说明

### Nuxt配置 (nuxt.config.ts)

**开发环境 - 代理所有API请求**
```typescript
devProxy: {
  '/api/**': {
    target: 'http://localhost:8001',
    changeOrigin: true  // 修改Host header
  }
}
```

**生产环境 - 后端直接handling**
```typescript
routeRules: {
  '/api/**': {
    proxy: process.env.API_BASE_URL 
      ? `${process.env.API_BASE_URL}/api/**` 
      : undefined  // 同域时不需要
  }
}
```

### 前端API客户端 (api/index.ts)

```typescript
// 始终使用相对路径！
const baseURL = ""  // 空字符串 = 相对路径

const api = axios.create({
  baseURL,
  withCredentials: true  // 允许发送cookies (跨域时)
})
```

**Why相对路径?**
- 开发环境: `/api/albums` → Nuxt代理 → 后端处理
- 生产环境: `/api/albums` → 后端直接处理
- **自动适应环境，无需修改代码!**

---

## 🎓 工作流详解

### 场景1: 用户登录

```
用户输入密码 → 点击登录
  ↓
前端 axios.post('/api/auth/login')
  ↓
[开发] Nuxt代理 → http://localhost:8001/api/auth/login
[生产] 直接访问 → https://domain.com/api/auth/login
  ↓
后端处理，返回JWT token
  ↓
前端拦截器自动设置 Authorization header:
  Authorization: Bearer <token>
  ↓
之后所有请求都携带token
```

### 场景2: 获取专辑列表

```
浏览器加载 http://localhost:5173/
  ↓
Nuxt页面渲染，调用 api.get('/api/admin/albums')
  ↓
[开发环境]
  请求 → Nuxt代理 (5173)
       → FastAPI (8001)
       → 返回JSON
       ← Nuxt返回浏览器
  
[生产环境]  
  请求 → FastAPI (8001)
       → 返回JSON

都无需CORS处理！
```

---

## 📋 常见问题解决

### Q1: 开发时仍然收到CORS错误?

**原因:** 可能有多个原因

```bash
# 检查1: Nuxt代理是否启动?
npm run dev  # 确保看到 "Listening on http://localhost:5173"

# 检查2: 后端地址是否正确?
# nuxt.config.ts 中的 API_BASE_URL 是否与实际后端地址匹配
echo $API_BASE_URL

# 检查3: 请求是否真的通过代理?
# 打开浏览器DevTools → Network，查看请求URL
# 应该是 http://localhost:5173/api/... 而不是 http://localhost:8001/api/...
```

**解决:**
```bash
# 重启Nuxt开发服务器
npm run dev

# 清除浏览器缓存和 localStorage
# DevTools → Application → Storage → Clear All
```

### Q2: 生产环境API返回404?

**原因:** 前端资源构建不完整

```bash
# 检查: 静态文件是否复制到后端?
ls backend/static/

# 重新构建
./build-frontend.sh  # 构建 + 复制到后端

# 启动后端
./start-backend.sh
```

### Q3: 在不同域名 (如 app.com) 访问API失败?

**解决:**
```bash
# 配置生产CORS
ALLOW_ORIGINS=https://app.com,https://api.app.com

# 或配置域名白名单
# .env
ALLOW_ORIGINS=https://yourdomain.com
```

### Q4: 跨域时cookies丢失?

**原因:** Axios没有设置 `withCredentials`

**检查:**
```typescript
// api/index.ts
const api = axios.create({
  withCredentials: true  // ✅ 必须有这一行
})
```

---

## 🔐 安全最佳实践

### 开发环境
```bash
ENV=development
ALLOW_ORIGINS=http://localhost:5173  # 仅本地前端
```

### 测试环境
```bash
ENV=testing
ALLOW_ORIGINS=https://staging.yourdomain.com
```

### 生产环境
```bash
ENV=production
ALLOW_ORIGINS=  # 空！使用同域部署
# 或多个前端应用：
# ALLOW_ORIGINS=https://app.com,https://admin.app.com
```

### Preflight缓存 (可选优化)
```python
# 在生产环境，可以缓存preflight请求
app.add_middleware(
    CORSMiddleware,
    # ...
    max_age=3600,  # 1小时缓存 → 减少OPTIONS请求
)
```

---

## 🧪 测试检查清单

### 开发环境测试

- [ ] `npm run dev` 启动Nuxt，无错误
- [ ] `python -m uvicorn app.main:app` 启动后端，无错误
- [ ] 访问 http://localhost:5173，页面加载
- [ ] 登录功能正常（API请求成功）
- [ ] 浏览器DevTools Network中看不到跨域错误
- [ ] 刷新页面，不会404（SPA路由正常）

### 生产环境测试

```bash
# 构建前端
./build-frontend.sh

# 启动后端（serving前端）
./start-backend.sh

# 访问
curl http://localhost:8001/  # 应返回HTML（前端index.html）
curl http://localhost:8001/api/health  # 应返回JSON

# 验证SPA路由
curl http://localhost:8001/albums/123  # 应返回HTML，不是404
```

---

## 📚 参考资源

### 相关概念
- [Same-Origin Policy](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)
- [CORS详解](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [SPA路由与服务器](https://nuxt.com/docs/guide/concepts/server-engine)

### 工具
- [Nuxt DevProxy文档](https://nuxt.com/docs/guide/concepts/server-engine#route-rules)
- [FastAPI CORS文档](https://fastapi.tiangolo.com/tutorial/cors/)
- [Axios拦截器](https://axios-http.com/docs/interceptors)

---

## 💡 总结

| 方面 | 开发环境 | 生产环境 |
|------|---------|---------|
| **前端地址** | localhost:5173 | yourdomain.com |
| **后端地址** | localhost:8001 | yourdomain.com |
| **API客户端** | `/api/**` → 代理 | `/api/**` → 同域 |
| **CORS需求** | 否（通过代理） | 否（同域） |
| **部署方式** | 前后端独立运行 | 后端serving前端 |

**关键收获:**
- 🎯 开发和生产使用同一份代码，自动适应环境
- 🚫 无需处理浏览器跨域问题
- 🔒 生产环境最安全（同域）
- 🚀 部署简单（一个后端服务）
