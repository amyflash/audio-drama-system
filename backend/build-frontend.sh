#!/bin/bash
# 前端构建并部署到后端静态目录

set -e

echo "========================================"
echo "🎨 前端构建工具"
echo "========================================"

# 进入前端目录
cd "$(dirname "$0")/../nuxt-frontend"

echo "📦 正在安装依赖..."
npm install --silent

# 设置 API 地址环境变量
export API_BASE_URL="http://36.50.84.162:8000"
export NUXT_PUBLIC_API_BASE_URL="http://36.50.84.162:8000"

echo "🔨 正在构建静态文件 (API: $API_BASE_URL)..."
npm run generate

echo "📁 正在复制静态文件到后端..."
BACKEND_STATIC="$(dirname "$0")/static"
mkdir -p "$BACKEND_STATIC"
rm -rf "$BACKEND_STATIC"/*
cp -r .output/public/* "$BACKEND_STATIC/"

echo ""
echo "========================================"
echo "✅ 前端构建完成！"
echo "========================================"
echo ""
echo "静态文件位置：$BACKEND_STATIC"
echo ""
echo "文件列表:"
ls -la "$BACKEND_STATIC"
echo ""
echo "重启后端服务以应用更改："
echo "  pkill -f 'uvicorn app.main:app'"
echo "  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
