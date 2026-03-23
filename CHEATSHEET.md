# 前后端分离 - 速查表

## 🚨 快速问题排查

### Q: 看到CORS错误？

```
Access to XMLHttpRequest at 'http://localhost:8001/...' 
from origin 'http://localhost:5173' has been blocked
```

**解决 (2分钟):**
```bash
# 1. 确保Nuxt在运行
npm run dev  # 应该看到 "Listening on http://localhost:5173"

# 2. 检查请求是否通过代理
# DevTools → Network → 看请求URL
# 应该是: http://localhost:5173/api/...
# 不应该是: http://localhost:8001/api/...

# 3. 如果还是出错，清除缓存
# DevTools → Application → Storage → Clear All
```

---

### Q: 生产部署后API返回404？

```bash
# 1. 确保前端已构建并复制
./build-frontend.sh

# 2. 检查静态文件
ls backend/static/index.html

# 3. 如果文件丢失，手动复制
cp -r nuxt-frontend/.output/public/* backend/static/

# 4. 启动后端
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

---

### Q: 登录后还是401？

**原因:** Authorization header没被发送

```typescript
// ✅ 检查 nuxt-frontend/api/index.ts

const api = axios.create({
  withCredentials: true  // 这一行必须有
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`  // 这一行必须有
  }
  return config
})
```

---

### Q: 刷新页面返回404？

```bash
# 检查1: Nuxt配置
grep "ssr:" nuxt-frontend/nuxt.config.ts  # 应该是 false

# 检查2: 后端SPAMiddleware
grep -A20 "class SPAMiddleware" backend/app/main.py
```

---

## 📋 环境变量配置速查

### 开发环境

```bash
# backend/.env
ENV=development
ALLOW_ORIGINS=

# nuxt-frontend/.env
API_BASE_URL=http://localhost:8001
NODE_ENV=development
```

### 生产环境

```bash
# backend/.env
ENV=production
ALLOW_ORIGINS=

# nuxt-frontend/.env
API_BASE_URL=
NODE_ENV=production
```

### 多前端应用

```bash
# backend/.env
ENV=production
ALLOW_ORIGINS=https://app.com,https://admin.app.com
```

---

## 🔍 调试命令

```bash
# 检查后端运行状态
curl http://localhost:8001/api/health

# 检查CORS配置
curl -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -X OPTIONS \
  http://localhost:8001/api/admin/albums -v

# 查看Axios请求
# DevTools → Network → 筛选 XHR
# 检查 Request Headers 中是否有 Authorization

# 查看localStorage
# DevTools → Application → Storage → localStorage
# 应该看到 token 键
```

---

## 🎯 API请求流程

### 开发环境

```
浏览器 → Nuxt (5173)
        ├─ 看到 /api/**
        ├─ 触发 devProxy
        └─ 转发到 FastAPI (8001)
           ↓
           处理请求
           ↓
        返回给 Nuxt
        ↓
浏览器收到数据
```

**关键:** 浏览器只看到 localhost:5173，不知道后端存在！

### 生产环境

```
浏览器 → FastAPI (8001)
        ├─ /api/** → 处理API
        └─ /      → 返回前端SPA
           ↓
           直接返回
           ↓
浏览器收到数据
```

**关键:** 同一域名，零跨域！

---

## 🔧 常用命令

```bash
# 开发
npm run dev                          # 启动Nuxt (5173)
python -m uvicorn app.main:app --reload  # 启动后端 (8001)

# 构建
npm run build                        # 构建前端
./build-frontend.sh                  # 构建+复制到后端

# 生产
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# 验证
curl http://localhost:8001/
curl http://localhost:8001/api/health
curl http://localhost:8001/albums/1
```

---

## 📊 配置矩阵速查

| ENV | ALLOW_ORIGINS | API_BASE_URL | 说明 |
|-----|---------------|--------------|------|
| development | (留空) | http://localhost:8001 | 自动config localhost |
| production | (留空) | (留空) | 同域，无需CORS |
| production | https://app.com | (留空) | 单个前端 |
| production | https://a.com,https://b.com | (留空) | 多个前端 |

---

## 💡 核心要点

### ✅ DO (要做的事)

- ✅ 前端API调用使用**相对路径** (`/api/...`)
- ✅ `ALLOW_ORIGINS` **留空** (自动配置)
- ✅ `API_BASE_URL` 开发指定，生产**留空**
- ✅ Axios配置 `withCredentials: true`
- ✅ 所有API请求通过**统一axios实例**
- ✅ **拦截器处理token** (自动添加)

### ❌ DON'T (不要做的事)

- ❌ 不要硬编码后端地址在前端
- ❌ 不要直接请求后端 (应通过代理)
- ❌ 不要在生产环境使用 `allow_origins=["*"]`
- ❌ 不要在生产环境指定 `API_BASE_URL`
- ❌ 不要忘记添加 `withCredentials: true`
- ❌ 不要在多个地方管理token

---

## 🧪 快速验证清单

### 开发环境验证

- [ ] `npm run dev` 启动无错误
- [ ] 访问 http://localhost:5173 页面加载
- [ ] 登录功能正常
- [ ] DevTools Network 无CORS错误
- [ ] 刷新页面不404

### 生产验证

- [ ] `./build-frontend.sh` 完成
- [ ] `python -m uvicorn app.main:app` 启动
- [ ] `curl http://localhost:8001/` 返回HTML
- [ ] `curl http://localhost:8001/api/health` 返回JSON
- [ ] `curl http://localhost:8001/albums/1` 返回HTML (SPA路由)

---

## 📞 需要帮助？

**查看完整文档:**
- `CORS_AND_ROUTING.md` - 深度技术解析
- `QUICK_START.md` - 详细操作指南
- `SOLUTION_SUMMARY.md` - 方案对比

**推荐阅读顺序:**
1. 本文件 (快速了解)
2. `QUICK_START.md` (学会使用)
3. `CORS_AND_ROUTING.md` (深入理解)

---

## 🎉 总结

| 方面 | 答案 |
|------|------|
| **跨域问题** | ✅ 完全解决 (代理+同域) |
| **路由问题** | ✅ 优雅处理 (SPA fallback) |
| **开发体验** | ✅ 最优 (热更新无需重启) |
| **生产部署** | ✅ 最简 (一个服务) |
| **安全性** | ✅ 最高 (同域无CORS) |

**你的项目: 🌟🌟🌟🌟🌟 (5星)**
