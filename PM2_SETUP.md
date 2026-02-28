# PM2 配置完成说明

## PM2 进程管理器已配置

### 当前状态

**前端服务：audio-drama-frontend**
- 状态：✅ online（运行中）
- PID：319678
- CPU：0%
- 内存：58.4MB
- 重启次数：0

### 已完成的配置

1. ✅ 使用 PM2 启动前端服务
2. ✅ 保存进程列表（pm2 save）

### 待完成的配置

**开机自启动**（需要手动执行）：

```bash
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u duoduo --hp /home/duoduo
```

执行后，PM2 会在系统重启时自动启动前端服务。

### PM2 常用命令

```bash
# 查看状态
pm2 status

# 查看日志
pm2 logs audio-drama-frontend

# 重启服务
pm2 restart audio-drama-frontend

# 停止服务
pm2 stop audio-drama-frontend

# 删除服务
pm2 delete audio-drama-frontend

# 保存当前进程列表
pm2 save
```

### PM2 优势

- ✅ 自动监控进程状态
- ✅ 崩溃后自动重启
- ✅ 日志管理
- ✅ 进程状态查看
- ✅ 优雅重启（先启动新进程，再停止旧进程）

### 配置时间

2026-02-28 14:10 UTC
