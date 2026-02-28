#!/bin/bash

# 极简广播剧系统脚本
# 用于重新部署整个系统

echo "🛑 停止所有容器..."
cd /home/duoduo/.openclaw/workspace/audio-drama-system
docker-compose down -v

echo "🏗️  重新构建后端镜像..."
docker-compose build backend

echo "🚀 启动服务..."
docker-compose up -d redis backend

echo "⏳ 等待服务启动..."
sleep 10

echo "📊 检查服务状态..."
docker-compose ps

echo "📋 查看后端日志..."
docker-compose logs backend --tail=20
