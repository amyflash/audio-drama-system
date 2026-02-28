#!/bin/bash
# 极简广播剧系统 - 启动脚本
# 确保前端和后端服务都正常运行

cd "$(dirname "$0")"

# 启动后端（Docker）
echo "🚀 启动后端服务..."
docker-compose up -d backend redis

# 等待后端启动
sleep 3

# 启动前端（Vite 开发服务器）
echo "🎨 启动前端服务..."
cd frontend

# 检查是否已有 Vite 进程
if pgrep -f "vite.*5173" > /dev/null; then
    echo "✅ 前端服务已在运行"
else
    # 使用 nohup 启动，确保在后台持续运行
    nohup npm run dev > /tmp/frontend.log 2>&1 &
    echo "✅ 前端服务已启动 (PID: $!)"

    # 等待 Vite 启动
    echo "⏳ 等待前端服务就绪..."
    for i in {1..30}; do
        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            echo "✅ 前端服务就绪"
            break
        fi
        sleep 1
    done
fi

# 检查服务状态
echo ""
echo "=== 服务状态 ==="
echo "📊 后端: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
echo "🎨 前端: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:5173/)"
echo "🌐 前端(外网): $(curl -s -o /dev/null -w '%{http_code}' https://q.1006868.xyz/)"
echo "🔧 后端(外网): $(curl -s -o /dev/null -w '%{http_code}' https://h.1006868.xyz/health)"
echo ""
echo "✅ 所有服务已启动！"
echo ""
echo "访问地址:"
echo "  - 前端: https://q.1006868.xyz"
echo "  - 后端: https://h.1006868.xyz/docs"
echo "  - 默认账号: admin / 123456"
