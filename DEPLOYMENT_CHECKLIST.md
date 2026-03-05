# 前后端整合部署检查清单

## 概述
此项目已配置为将前端（Nuxt 3）打包成静态文件，并挂载到 FastAPI 后端，实现单容器部署。

## 修改的文件

### 1. 前端配置 (`nuxt-frontend/nuxt.config.ts`)
- 设置 `ssr: false` - 禁用服务器端渲染，生成静态 SPA
- 设置 `apiBaseUrl: ''` - 使用相对路径访问 API

### 2. 后端配置 (`backend/app/main.py`)
- 添加静态文件服务：`app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")`
- 静态文件目录：`/app/static` (构建后生成)

### 3. 构建配置
- `Dockerfile.combined` - 多阶段构建，集成前端静态文件
- `docker-compose.yml` - 更新为单服务架构

## 服务器部署步骤

### 1. 上传文件到服务器
```bash
# 将整个项目上传到服务器
scp -r audio-drama-system user@your-server:/path/to/
```

### 2. 构建并启动容器
```bash
cd /path/to/audio-drama-system
docker-compose up -d --build
```

### 3. 验证部署

#### 检查容器状态
```bash
docker ps
# 应看到 audio-drama-combined 容器运行在 8000 端口
```

#### 测试访问
1. **前端页面**: http://your-server:8000
2. **API 文档**: http://your-server:8000/docs
3. **健康检查**: http://your-server:8000/api/health
4. **静态文件**: http://your-server:8000/_nuxt/  (应返回文件而不是 404)

#### 测试功能
1. 登录页面：`/login`
2. 专辑列表：`/`
3. 专辑详情：`/albums/{id}`
4. 播放器：`/player/{id}`

#### 检查日志
```bash
docker logs audio-drama-combined
# 应看到以下信息：
# ✅ 已挂载静态文件目录: /app/static
# 🚀 正在初始化应用...
# ✅ 应用初始化完成
```

## 故障排除

### 问题1: 前端页面显示 404
**原因**: 静态文件未正确构建或挂载
**解决**:
1. 检查容器内是否有 `/app/static` 目录
   ```bash
   docker exec audio-drama-combined ls -la /app/static/
   ```
2. 确认有 `index.html` 文件
3. 重建容器：`docker-compose down && docker-compose up -d --build`

### 问题2: API 请求失败
**原因**: 前端配置的 API 路径不正确
**解决**:
1. 检查浏览器开发者工具中的网络请求
2. 确认 API 请求路径为相对路径（如 `/api/auth/login`）
3. 验证 FastAPI 日志中是否有 API 请求

### 问题3: 路由刷新 404
**原因**: SPA 路由需要后端支持
**解决**:
- FastAPI 已配置 `StaticFiles(html=True)`，会自动返回 `index.html` 处理客户端路由
- 确认配置正确

## 回滚到传统部署
如果需要回滚到传统的前后端分离部署：

1. 恢复 `docker-compose.yml` 到原始版本（两个服务）
2. 恢复 `nuxt-frontend/nuxt.config.ts` 中的 `ssr` 和 `apiBaseUrl` 设置
3. 使用原始的 `Dockerfile` 文件

## 优势总结
1. **简化运维**: 只需管理一个容器
2. **避免跨域**: 前后端同源，无需 CORS 配置
3. **统一入口**: 所有流量通过同一端口
4. **资源节省**: 减少一个容器运行的开销
5. **部署简单**: 一条命令即可部署完整应用