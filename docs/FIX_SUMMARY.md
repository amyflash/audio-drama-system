# 错误修复与部署方案总结

## ✅ 已修复的问题

### 1. 数据库目录不存在
**问题:** `data/` 目录不存在导致 SQLite 无法创建数据库文件  
**修复:** 
- 在 `app/db/init_db.py` 中自动创建目录
- 在 `init.sh` 中创建目录

### 2. 缺少数据库初始化脚本
**问题:** 没有独立的 Python 初始化脚本  
**修复:** 创建 `backend/app/db/init_db.py`，支持：
- 创建所有数据库表
- 创建索引
- 创建视图
- 创建默认管理员账号
- 支持 `--reset` 参数重置数据库

### 3. 前端静态文件挂载
**问题:** 前端路由转发配置复杂  
**修复:** 
- 前端使用 `npm run generate` 生成静态文件
- 后端直接挂载 `static/` 目录

### 4. API 路由被静态文件覆盖
**问题:** `app.mount("/", StaticFiles(...))` 导致 `/api/health` 等接口返回 404  
**修复:** 
- 将所有 `@app.get("/api/...")` 路由定义移到 `app.mount()` 之前
- 确保 API 路由优先匹配

## 📁 新增文件

| 文件 | 说明 |
|------|------|
| `backend/app/db/init_db.py` | SQLite 初始化脚本 |
| `backend/init.sh` | 一键初始化 Shell 脚本 |
| `backend/build-frontend.sh` | 前端构建脚本 |
| `.env.example` | 环境变量模板 |
| `README.md` | 项目说明文档 |

## 🚀 快速部署

### 步骤 1：环境准备

```bash
# 安装 Python 3.10+ 和 Node.js 18+
python3 --version
node --version
```

### 步骤 2：后端初始化

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（创建表、索引、默认管理员）
./init.sh
```

### 步骤 3：前端构建

```bash
# 在后端目录执行
./build-frontend.sh
```

### 步骤 4：启动服务

```bash
# 停止旧进程（如有）
pkill -f "uvicorn app.main:app"

# 启动后端（包含前端静态文件）
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000

## 📋 初始化 SQLite 数据库

### 方法一：使用 Shell 脚本（推荐）

```bash
cd backend
./init.sh
```

### 方法二：使用 Python 模块

```bash
cd backend
source venv/bin/activate
python -m app.db.init_db
```

### 方法三：重置数据库

```bash
cd backend
source venv/bin/activate
python -m app.db.init_db --reset
```

## 📊 数据库结构

### 表结构

| 表名 | 说明 | 字段数 |
|------|------|--------|
| `users` | 用户表 | 7 |
| `albums` | 专辑表 | 8 |
| `episodes` | 单集表 | 8 |
| `sessions` | 会话审计表 | 7 |

### 视图

| 视图名 | 说明 |
|--------|------|
| `album_detail` | 专辑详情（含剧集统计） |

### 索引

- `idx_users_username` - 用户名快速查询
- `idx_albums_sort_order` - 专辑排序
- `idx_episodes_album_id` - 剧集关联专辑
- `idx_episodes_sort_order` - 剧集排序
- `idx_sessions_token` - Session Token 查询
- `idx_sessions_user_id` - Session 用户查询

## 🔑 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | 123456 | admin |

⚠️ **首次登录后请立即修改密码！**

## 🔧 运维管理

### 常用命令

```bash
# 启动后端
cd backend && source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 构建前端
cd backend && ./build-frontend.sh

# 备份数据库
cp backend/data/audio_drama.db backup/audio_drama_$(date +%Y%m%d).db

# 查看进程
ps aux | grep uvicorn

# 停止服务
pkill -f "uvicorn app.main:app"
```

### 生产环境配置

使用 systemd 管理后端服务：

创建 `/etc/systemd/system/audio-drama.service`：

```ini
[Unit]
Description=Audio Drama Backend Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/audio-drama-system/backend
Environment="PATH=/path/to/audio-drama-system/backend/venv/bin"
ExecStart=/path/to/audio-drama-system/backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable audio-drama
sudo systemctl start audio-drama
sudo systemctl status audio-drama
```

### Nginx 反向代理（可选）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 🆘 故障排查

### 数据库锁定
```bash
# 重启后端服务
pkill -f "uvicorn app.main:app"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 服务无法启动
```bash
# 检查端口占用
netstat -tlnp | grep 8000

# 查看日志
journalctl -u audio-drama -f  # systemd 方式
```

### 重新初始化
```bash
# 删除数据库
rm backend/data/audio_drama.db

# 重新初始化
./init.sh
```

### 前端无法访问
```bash
# 检查静态文件是否存在
ls -la backend/static/

# 重新构建前端
./build-frontend.sh
```

## 📖 相关文档

- [README.md](../README.md) - 项目说明
- [PRD.md](PRD.md) - 产品需求文档
- [TSD.md](TSD.md) - 技术方案文档
