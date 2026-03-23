# 极简广播剧系统

基于 FastAPI + Nuxt 3 的音频剧管理与播放系统，**集成 JWT-Auth SSO 单点登录**。

## 📚 文档导航

> **新手？** 按以下顺序阅读文档，5分钟上手！

| 文档 | 用途 | 阅读时间 |
|------|------|--------|
| **[README.md](./README.md)** (本文件) | 📖 项目首页和概览 | 3分钟 |
| **[QUICK_START.md](./QUICK_START.md)** | 🚀 快速开始指南 | 10分钟 |
| **[CHEATSHEET.md](./CHEATSHEET.md)** | ⚡ 问题快速排查 | 2分钟 |
| **[SSO_INTEGRATION.md](./SSO_INTEGRATION.md)** | 🔐 JWT-Auth SSO集成 | 15分钟 |
| **[CORS_AND_ROUTING.md](./CORS_AND_ROUTING.md)** | 🔗 跨域解决方案深度解析 | 15分钟 |
| **[SOLUTION_SUMMARY.md](./SOLUTION_SUMMARY.md)** | 💡 4种方案对比分析 | 10分钟 |

### 推荐学习路径

```
第一次使用?
└─ QUICK_START.md (5分钟启动项目)
   └─ 遇到问题查 CHEATSHEET.md

想集成或了解SSO?
└─ SSO_INTEGRATION.md (完整SSO指南)
   ├─ 包括开发和生产配置
   ├─ 包括多个SSO场景
   └─ 包括常见问题排查

想深入理解跨域?
└─ CORS_AND_ROUTING.md (技术深度解析)
   ├─ 原理讲解
   ├─ 4种方案对比
   └─ 安全最佳实践

想了解设计选择?
└─ SOLUTION_SUMMARY.md (方案对比分析)
   ├─ 现状评估
   └─ 为什么优雅
```

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户浏览器                               │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Nuxt Dev服务器 (开发: 5173)                    │
│              或 后端 (生产: 8001)                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                    ┌─────┴─────┐
                    ▼           ▼
        ┌──────────────┐  ┌──────────────┐
        │ FastAPI (开发) │  │ jwt-auth SSO │
        │   8001       │  │   8000       │
        └──────────────┘  └──────────────┘
```

**关键特性:**
- ✅ **零跨域问题** - 使用代理模式 (开发) + 同域部署 (生产)
- ✅ **优雅路由** - SPA客户端路由 + 服务器fallback
- ✅ **单点登录** - SSO认证 + JWT令牌
- ✅ **简单部署** - 一个后端服务运行一切

---

## 部署架构

- **jwt-auth**: 端口 8000，提供用户认证服务
- **音频剧系统**: 端口 8001，提供业务功能
  - 开发: Nuxt在5173，代理API到8001
  - 生产: 后端同时serve前端SPA和API
- **SSO对接**: 音频剧系统验证 jwt-auth 签发的 token

---

## 🚀 5分钟快速启动

### Step 1: 配置环境变量

```bash
# 后端配置
cd backend
cp .env.example .env
# 编辑 .env，确保以下配置
# ENV=development
# ALLOW_ORIGINS=  (留空，自动配置)

# 前端配置
cd ../nuxt-frontend
cp .env.example .env
# 编辑 .env，确保以下配置
# API_BASE_URL=http://localhost:8001
```

### Step 2: 启动服务

```bash
# 终端1 - 启动前端
cd nuxt-frontend
npm run dev  # 访问 http://localhost:5173

# 终端2 - 启动后端
cd backend
python -m uvicorn app.main:app --reload  # 端口 8001
```

### Step 3: 验证

- 访问 http://localhost:5173
- 登录测试 (admin / 123456)
- DevTools检查 Network，应该无CORS错误 ✅

---

## 开发指南

| 脚本 | 用途 | 端口 |
|------|------|------|
| `npm run dev` (前端目录) | 前端开发服务器 (热重载) | 5173 |
| `python -m uvicorn app.main:app --reload` (后端目录) | 后端服务 (热重载) | 8001 |
| `./build-frontend.sh` | 构建前端+复制到后端 | - |

### 开发环境 (推荐)

```bash
# 终端1
cd nuxt-frontend && npm run dev

# 终端2
cd backend && python -m uvicorn app.main:app --reload
```

### 一键启动 (可选)

```bash
./start-all.sh  # 构建前端 + 启动后端
```

---

## 生产部署

### 构建

```bash
# 构建前端并复制到后端
./build-frontend.sh
```

### 启动

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 验证

```bash
# 前端SPA
curl http://localhost:8001/

# API正常
curl http://localhost:8001/api/health

# SPA路由正常 (应返回HTML，不是404)
curl http://localhost:8001/albums/123
```

---

## 🔗 跨域与路由解决方案

### 问题

前后端分离自然带来跨域和路由问题。

### 解决方案

我们采用了**最优雅的混合方案**:

| 环境 | 方案 | 效果 |
|------|------|------|
| **开发** | Nuxt代理所有API请求 | 零跨域，浏览器看不到后端 |
| **生产** | 后端同时serve前端+API | 完全同域，浏览器只看一个地址 |

**核心好处:**
- ✅ 无需复杂的CORS配置
- ✅ 开发生产代码完全一致
- ✅ 部署只需一个服务
- ✅ 生产环境最安全

### 工作原理

**开发环境:**
```
浏览器 → localhost:5173 (Nuxt)
         ↓ (代理 /api/**)
      localhost:8001 (FastAPI)
      ↓ (返回)
浏览器 ← localhost:5173 (Nuxt)
```

**生产环境:**
```
浏览器 → localhost:8001 (FastAPI)
      ├─ /api/** (处理)
      └─ / (serve SPA)
```

**更多信息:** 见 [QUICK_START.md](./QUICK_START.md) 和 [CORS_AND_ROUTING.md](./CORS_AND_ROUTING.md)

---

## 默认账号

- 用户名: `admin`
- 密码: `123456`

---

## 常见问题

### 看到CORS错误？

```
❌ Access to XMLHttpRequest at 'http://localhost:8001/...' 
   from origin 'http://localhost:5173' has been blocked by CORS
```

**解决:** 检查Nuxt是否启动 + 浏览器缓存清除

详见 [CHEATSHEET.md](./CHEATSHEET.md)

### 生产部署后API返回404？

**解决:** 确保前端已构建并复制到后端

```bash
./build-frontend.sh
```

### 刷新页面返回404？

**解决:** 这是SPA路由问题，后端SPAMiddleware已处理

如问题仍存在，检查 `backend/app/main.py` 中的 `SPAMiddleware`

---

## 项目结构

```
audio-drama-system/
├── backend/                    # FastAPI后端
│   ├── app/
│   │   ├── main.py            # FastAPI应用入口
│   │   ├── models/            # 数据模型
│   │   ├── api/               # API路由
│   │   ├── core/              # 配置管理
│   │   └── db/                # 数据库
│   ├── static/                # 前端构建输出
│   ├── .env                   # 环境变量
│   └── requirements.txt        # Python依赖
├── nuxt-frontend/             # Nuxt 3前端
│   ├── pages/                 # 页面路由
│   ├── api/                   # API客户端
│   ├── components/            # Vue组件
│   ├── nuxt.config.ts         # Nuxt配置
│   └── package.json           # Node依赖
├── CHEATSHEET.md              # ⚡ 问题速查
├── QUICK_START.md             # 🚀 快速上手
├── CORS_AND_ROUTING.md        # 🔗 深度解析
└── SOLUTION_SUMMARY.md        # 💡 方案对比
```

---

## 技术栈

**后端:**
- FastAPI 0.104+
- SQLAlchemy ORM
- SQLite 数据库
- Pydantic 数据验证
- JWT 认证

**前端:**
- Nuxt 3
- Vue 3
- TypeScript
- Tailwind CSS
- Axios

---

## 环境变量配置

### 后端 (`backend/.env`)

```bash
# 运行环境 (开发/测试/生产)
ENV=development

# CORS配置 (推荐留空)
ALLOW_ORIGINS=

# 其他配置 (见 .env.example)
DATABASE_URL=sqlite:///./data/audio_drama.db
SSO_ENABLED=true
SSO_JWT_AUTH_URL=http://localhost:8000
# ...
```

### 前端 (`nuxt-frontend/.env`)

```bash
# 后端地址 (开发指定，生产留空)
API_BASE_URL=http://localhost:8001

# Node环境
NODE_ENV=development
```

详见各目录的 `.env.example`

---

## 学习资源

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [Nuxt官方文档](https://nuxt.com/docs)
- [CORS详解 (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [SPA路由原理](https://developer.mozilla.org/en-US/docs/Glossary/SPA)

---

## 反馈与贡献

有问题或建议？请提交Issue或Pull Request。

---

**最后更新:** 2024年3月  
**版本:** 1.0.0

