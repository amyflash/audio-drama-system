#!/bin/bash
# 前端开发服务器（需要后端在 8001 端口运行）
# API 请求会被代理到 http://localhost:8001

cd "$(dirname "$0")/nuxt-frontend"
export API_BASE_URL="http://localhost:8001"
npm run dev
