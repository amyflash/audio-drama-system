# 极简广播剧管理与在线收听系统
# 部署与运维文档

**项目名称：** 极简广播剧管理与在线收听系统
**版本号：** V1.0.0
**文档编写日期：** 2026-02-28
**文档状态：** 正式发布

---

## 1. 环境要求

### 1.1 硬件要求

| 配置 | 最低要求 | 推荐配置 |
| :--- | :--- | :--- |
| **CPU** | 2 核 | 4 核 |
| **内存** | 4GB | 8GB |
| **存储** | 50GB | 100GB+ |
| **带宽** | 10Mbps | 50Mbps+ |

**说明：**
- 音频文件占用大量存储，建议预留至少 50GB
- 10 人同时播放需要至少 20Mbps 带宽（按 MP3 128kbps 算）

---

### 1.2 软件要求

| 软件 | 版本要求 |
| :--- | :--- |
| **操作系统** | Ubuntu 22.04 LTS / Debian 11 / CentOS 8 |
| **Docker** | 20.10+ |
| **Docker Compose** | 2.0+ |
| **Nginx** | 1.24+（可选，若使用外部 Nginx） |
| **域名** | 需要已解析到 VPS IP |
| **SSL 证书** | Let's Encrypt（推荐）或自签名 |

---

## 2. 快速部署

### 2.1 一键部署脚本

```bash
#!/bin/bash
# deploy.sh - 一键部署脚本

set -e

echo "=== 极简广播剧系统 - 快速部署 ==="

# 1. 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "Docker 未安装，正在安装..."
    curl -fsSL https://get.docker.com | bash
    sudo usermod -aG docker $USER
fi

# 2. 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose 未安装，正在安装..."
    sudo apt update
    sudo apt install -y docker-compose
fi

# 3. 拉取代码
if [ ! -d "audio-drama-system" ]; then
    git clone https://github.com/your-repo/audio-drama-system.git
fi

cd audio-drama-system

# 4. 配置环境变量
cat > .env << EOF
# 域名配置
DOMAIN=your-domain.com

# 数据库配置
DATABASE_URL=sqlite:///./data/audio_drama.db

# Redis 配置
REDIS_URL=redis://redis:6379/0

# 密钥配置
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# 业务配置
MAX_CONCURRENT_USERS=10
SESSION_EXPIRE_SECONDS=1800
UPLOAD_MAX_FILE_SIZE=104857600  # 100MB

# 管理员初始密码
DEFAULT_ADMIN_PASSWORD=123456

# SSL 证书
SSL_CERT_PATH=./certs/fullchain.pem
SSL_KEY_PATH=./certs/privkey.pem
EOF

echo "✅ 环境变量配置完成"

# 5. 生成 SSL 证书（使用 Let's Encrypt）
read -p "是否需要配置 HTTPS？(y/n) " use_ssl
if [ "$use_ssl" == "y" ]; then
    read -p "请输入域名（如：audio.example.com）: " domain

    # 使用 Certbot 获取证书
    sudo apt install -y certbot
    sudo certbot certonly --standalone -d $domain

    # 复制证书到项目目录
    sudo cp /etc/letsencrypt/live/$domain/fullchain.pem ./certs/
    sudo cp /etc/letsencrypt/live/$domain/privkey.pem ./certs/
    sudo chown $USER:$USER ./certs/*.pem

    sed -i "s/DOMAIN=.*/DOMAIN=$domain/" .env
fi

# 6. 构建并启动服务
echo "正在构建 Docker 镜像..."
docker-compose build

echo "正在启动服务..."
docker-compose up -d

# 7. 等待服务启动
echo "等待服务启动（约 30 秒）..."
sleep 30

# 8. 检查服务状态
echo "=== 服务状态 ==="
docker-compose ps

# 9. 初始化数据库
echo "正在初始化数据库..."
docker-compose exec backend python -c "from app.db.init_db import init_db; init_db()"

echo ""
echo "=== 部署成功！ ==="
echo ""
echo "访问地址："
if [ "$use_ssl" == "y" ]; then
    echo "  HTTPS: https://$domain"
else
    echo "  HTTP: http://your-domain.com"
fi
echo ""
echo "默认管理员账号："
echo "  用户名: admin"
echo "  密码: 123456（请在登录后立即修改！）"
echo ""
echo "日志查看："
echo "  docker-compose logs -f"
echo ""
```

**使用方法：**
```bash
chmod +x deploy.sh
./deploy.sh
```

---

### 2.2 手动部署

#### 步骤 1：安装 Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# CentOS
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
```

#### 步骤 2：安装 Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 步骤 3：克隆代码

```bash
git clone https://github.com/your-repo/audio-drama-system.git
cd audio-drama-system
```

#### 步骤 4：配置环境变量

```bash
cp .env.example .env
nano .env
```

**修改 `.env` 文件：**
```bash
DOMAIN=your-domain.com
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
MAX_CONCURRENT_USERS=10
DEFAULT_ADMIN_PASSWORD=123456
```

#### 步骤 5：构建并启动

```bash
docker-compose build
docker-compose up -d
```

#### 步骤 6：初始化数据库

```bash
docker-compose exec backend python -c "from app.db.init_db import init_db; init_db()"
```

#### 步骤 7：访问系统

- 前端：http://your-domain.com
- 后端 API：http://your-domain.com/api
- Swagger 文档：http://your-domain.com/docs

---

## 3. 配置 HTTPS（生产环境推荐）

### 3.1 使用 Let's Encrypt

```bash
# 安装 Certbot
sudo apt update
sudo apt install -y certbot

# 生成证书（需要已解析域名）
sudo certbot certonly --standalone -d your-domain.com

# 复制证书
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./certs/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./certs/
sudo chown $USER:$USER ./certs/*.pem
```

### 3.2 配置 Nginx（HTTPS）

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

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
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 禁止直接访问音频文件
    location /media {
        internal;
        alias /media;
        deny all;
    }
}
```

### 3.3 自动续签证书

```bash
# 添加 Cron 任务（每天凌晨 3 点检查）
0 3 * * * certbot renew --quiet && docker-compose restart frontend
```

---

## 4. 运维管理

### 4.1 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 进入后端容器
docker-compose exec backend bash

# 进入 Redis 容器
docker-compose exec redis redis-cli

# 更新代码并重启
git pull
docker-compose build
docker-compose up -d
```

---

### 4.2 数据库备份

#### 手动备份

```bash
# 备份数据库
docker-compose exec backend python -c "
from datetime import datetime
import shutil
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copy('data/audio_drama.db', f'backup/audio_drama_{timestamp}.db')
print('备份成功')
"
```

#### 自动备份

```bash
# 创建 Cron 任务
0 3 * * * cd /path/to/audio-drama-system && docker-compose exec backend python scripts/backup.py
```

**备份脚本 (`scripts/backup.py`)：**
```python
from datetime import datetime
import os
import shutil

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
source = '/app/data/audio_drama.db'
backup_dir = '/app/backup'
os.makedirs(backup_dir, exist_ok=True)
backup_file = f'{backup_dir}/audio_drama_{timestamp}.db'

shutil.copy(source, backup_file)

# 删除 7 天前的备份
for file in os.listdir(backup_dir):
    file_path = os.path.join(backup_dir, file)
    if os.path.getmtime(file_path) < (datetime.now().timestamp() - 7 * 86400):
        os.remove(file_path)

print(f'备份成功: {backup_file}')
```

---

### 4.3 数据恢复

```bash
# 停止服务
docker-compose stop backend

# 恢复数据库
docker-compose exec backend cp backup/audio_drama_20260228_030000.db data/audio_drama.db

# 重启服务
docker-compose start backend
```

---

### 4.4 监控在线人数

```bash
# 查看 Redis 中的当前 Session 数
docker-compose exec redis redis-cli keys "session:*" | wc -l
```

**输出示例：**
```
7
# 表示当前有 7 人在线
```

---

### 4.5 清理过期 Session

Redis 的 TTL 会自动过期 Session，无需手动清理。但如需强制清理：

```bash
# 清除所有 Session
docker-compose exec redis redis-cli --scan --pattern 'session:*' | xargs redis-cli del
```

---

## 5. 性能优化

### 5.1 音频压缩

上传前建议压缩音频：

```bash
# 使用 FFmpeg 压缩 MP3（128kbps）
ffmpeg -i input.wav -codec:a libmp3lame -b:a 128k -ar 44100 output.mp3
```

### 5.2 静态资源 CDN

将图片和前端静态资源上传到 CDN，减轻服务器压力。

### 5.3 Redis 持久化

在 `docker-compose.yml` 中启用 Redis AOF 持久化：

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes
  volumes:
    - redis_data:/data
```

---

## 6. 故障排查

### 6.1 服务无法启动

```bash
# 查看服务状态
docker-compose ps

# 查看容器日志
docker-compose logs backend
docker-compose logs frontend
```

**常见问题：**

| 错误信息 | 原因 | 解决方案 |
| :--- | :--- | :--- |
| `Connection refused` | 后端服务未启动 | `docker-compose restart backend` |
| `SSL certificate error` | 证书过期或路径错误 | 检查证书路径，重新申请 |
| `Database locked` | SQLite 文件被占用 | 重启后端服务 |

---

### 6.2 音频无法播放

**排查步骤：**

1. 检查文件是否存在：
```bash
docker-compose exec backend ls -lh /media/albums/1/
```

2. 检查 Token 是否有效：
```javascript
// 浏览器控制台
console.log(localStorage.getItem('token'))
```

3. 查看 Nginx 日志：
```bash
docker-compose logs frontend
```

---

### 6.3 在线人数控制失效

**排查步骤：**

1. 检查 Redis 是否正常：
```bash
docker-compose exec redis redis-cli ping
# 应输出 PONG
```

2. 查看 Session 数据：
```bash
docker-compose exec redis redis-cli --scan --pattern 'session:*'
```

3. 检查 Redis TTL：
```bash
docker-compose exec redis redis-cli TTL "session:1"
# 应返回剩余秒数
```

---

## 7. 安全加固

### 7.1 修改默认密码

首次登录后立即修改 admin 密码：

```bash
docker-compose exec backend python -c "
from app.core.security import hash_password
from app.db.session import SessionLocal
db = SessionLocal()
# 更新密码逻辑...
"
```

### 7.2 防火墙配置

```bash
# Ubuntu UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 7.3 定期更新

```bash
# 更新 Docker 镜像
docker-compose pull
docker-compose up -d

# 更新系统包
sudo apt update && sudo apt upgrade
```

---

## 8. 版本升级

### 8.1 备份数据

```bash
# 备份数据库
docker-compose exec backend python scripts/backup.py

# 备份音频文件
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

### 8.2 升级步骤

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 构建新版本
docker-compose build

# 3. 停止旧服务
docker-compose down

# 4. 启动新服务
docker-compose up -d

# 5. 检查服务状态
docker-compose ps
```

---

## 9. 成本估算

### 9.1 服务器成本（阿里云/腾讯云为例）

| 配置 | 价格（月） | 说明 |
| :--- | :--- | :--- |
| 2 核 4GB 50GB | ¥100-150 | 满足最低需求 |
| 4 核 8GB 100GB | ¥200-300 | 推荐 |
| 带宽 20Mbps | ¥50-100 | 按流量计费更便宜 |

**年度预算：** ¥1800-3600

### 9.2 域名成本

- .com 域名：¥80-120/年
- Let's HTTPS：免费

**总计：** ¥1900-3700/年（含服务器、域名、HTTPS）

---

## 10. 联系与支持

---

| 联系方式 | 说明 |
| :--- | :--- |
| **GitHub Issues** | https://github.com/your-repo/issues |
| **文档** | https://docs.audio-drama-system.com |
| **邮件** | support@example.com |

---

## 11. 变更记录

| 版本 | 日期 | 变更内容 | 作者 |
| :--- | :--- | :--- | :--- |
| V1.0.0 | 2026-02-28 | 初始版本 | AI |
