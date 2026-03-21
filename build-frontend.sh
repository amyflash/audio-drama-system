#!/bin/bash
# 构建前端并复制到后端静态目录

cd "$(dirname "$0")"

echo "📦 构建前端静态文件..."
cd nuxt-frontend
npm run generate

echo "📁 复制静态文件到后端..."
mkdir -p ../backend/static
rm -rf ../backend/static/*
cp -r .output/public/* ../backend/static/

echo "✅ 前端构建完成！"
echo "📍 静态文件位置: backend/static/"
