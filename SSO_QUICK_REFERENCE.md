# SSO 快速参考卡

## 🎯 1分钟快速理解

### SSO是什么？

**统一认证中心:**
```
多个应用 ← 用户一次登录 → jwt-auth SSO服务
  ├─ 音频剧系统
  ├─ 其他应用
  └─ 后台管理
```

### 你的项目中的SSO

```
用户登录
  ↓
前端请求 /api/auth/login
  ↓
FastAPI转发到 jwt-auth (8000)
  ↓
jwt-auth验证用户，返回JWT token
  ↓
前端保存token到localStorage
  ↓
后续请求自动添加: Authorization: Bearer <token>
  ↓
FastAPI自动验证token ✅
```

---

## ⚙️ 5分钟快速配置

### Step 1: 获取SSO密钥

```bash
# 查看jwt-auth的密钥
cat shared/sso_client/.env | grep SECRET_KEY

# 复制值，例如:
# Ck-ZbtbR-sdSnQjUroh2q_-joNuUreJtfAnRnqeKFCJgaBvWRbHN6hKscrXxg9bP__KQ_Yl_sDFVu1iG1PlKHg
```

### Step 2: 配置后端

**backend/.env**
```bash
# 复制上面的值
SSO_SECRET_KEY=Ck-ZbtbR-sdSnQjUroh2q_-joNuUreJtfAnRnqeKFCJgaBvWRbHN6hKscrXxg9bP__KQ_Yl_sDFVu1iG1PlKHg

# 其他配置保持默认
SSO_ENABLED=true
SSO_JWT_AUTH_URL=http://localhost:8000
SSO_ALGORITHM=HS256
ENV=development
```

### Step 3: 启动服务

```bash
# 终端1 - jwt-auth SSO
cd shared/sso_client
python -m uvicorn app.main:app --port 8000

# 终端2 - 后端
cd backend
python -m uvicorn app.main:app --port 8001

# 终端3 - 前端
cd nuxt-frontend
npm run dev
```

### Step 4: 测试

```bash
# 访问前端
http://localhost:5173

# 点击登录，输入:
用户名: admin
密码: 123456

# 应该登录成功！✅
```

---

## 🔐 关键概念速查

| 概念 | 说明 | 例子 |
|------|------|------|
| **SSO** | 单点登录 | jwt-auth服务 |
| **JWT** | JSON Web Token | eyJhbGc... |
| **Secret Key** | 加密密钥 | Ck-Zbt... |
| **Token** | 用户身份凭证 | localStorage中存储 |
| **Bearer** | Token认证方式 | Authorization: Bearer <token> |

---

## 🚀 开发vs生产对比

| 场景 | 地址 | CORS | SSO | 结果 |
|------|------|------|-----|------|
| **开发** | localhost | 自动允许 | localhost:8000 | ✅ 正常 |
| **生产** | yourdomain.com | 禁用 | 内网:8000 | ✅ 最优 |

---

## ❓ 常见问题

### Q: Token是什么？

**A:** 用户登录后服务器签发的凭证，格式如下：

```
Header.Payload.Signature
↓      ↓        ↓
算法  用户信息  验证签名

例如: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP...
```

### Q: 怎样验证SSO是否工作？

**A:** 三个检查：

```bash
# 1. 检查jwt-auth是否运行
curl http://localhost:8000/health

# 2. 检查能否登录
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'
# 应该返回 access_token

# 3. 使用token调用受保护API
curl -X GET http://localhost:8001/api/admin/albums \
  -H "Authorization: Bearer <上面返回的token>"
# 应该返回数据
```

### Q: SSO_SECRET_KEY错了会怎样？

**A:** 登录时token无法验证，返回401：

```json
{
  "detail": "Could not validate credentials"
}
```

**解决:** 确保和jwt-auth的SECRET_KEY一致

### Q: 生产环境怎样配置SSO？

**A:** 使用环境变量注入：

```bash
docker run \
  -e SSO_SECRET_KEY="..." \
  -e SSO_JWT_AUTH_URL="http://jwt-auth:8000" \
  audio-drama-system:latest
```

---

## 📋 配置检查清单

- [ ] 获取了jwt-auth的SECRET_KEY
- [ ] 配置了backend/.env中的SSO_SECRET_KEY
- [ ] SSO_JWT_AUTH_URL指向正确的jwt-auth地址
- [ ] 启动了jwt-auth服务
- [ ] 启动了FastAPI后端
- [ ] 能够成功登录
- [ ] 能够调用受保护的API
- [ ] Token自动包含在请求headers中
- [ ] 前端localStorage有token
- [ ] 生产环境使用环境变量注入SSO配置

---

## 🔗 相关资源

- **完整SSO文档:** [SSO_INTEGRATION.md](./SSO_INTEGRATION.md)
- **快速开始:** [QUICK_START.md](./QUICK_START.md)
- **CORS与SSO:** [CORS_AND_ROUTING.md](./CORS_AND_ROUTING.md)

---

## 💡 核心要点

```
1️⃣ SSO密钥必须相同
   backend/.env 的 SSO_SECRET_KEY
   = jwt-auth 的 SECRET_KEY

2️⃣ Token自动管理
   前端自动添加到所有请求
   后端自动验证

3️⃣ 跨域无需处理
   开发: Nuxt代理处理
   生产: 同域无跨域

4️⃣ 最简配置
   ENV=development
   ALLOW_ORIGINS=  (留空自动配置)
```

**就这么简单！** ✨
