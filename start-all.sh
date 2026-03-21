#!/bin/bash
# 音频剧系统 - 完整启动脚本
# 前提：已完成前端构建（npm run generate + 复制到backend/static）

cd "$(dirname "$0")"

echo "🚀 启动音频剧系统..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 jwt-auth 服务: http://localhost:8000"
echo "📍 音频剧系统:    http://localhost:8001"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 启动后端
echo ""
echo "🔧 启动后端服务 (端口 8001)..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
