#!/bin/bash
# PM2 Nuxt 前端服务管理脚本

APP_NAME="audio-drama-nuxt"
ECOSYSTEM_CONFIG="/home/duoduo/.openclaw/workspace/audio-drama-system/ecosystem-nuxt.config.js"

case "$1" in
  start)
    echo "启动 Nuxt 前端服务..."
    pm2 start "$ECOSYSTEM_CONFIG"
    ;;
  stop)
    echo "停止 Nuxt 前端服务..."
    pm2 stop "$APP_NAME"
    ;;
  restart)
    echo "重启 Nuxt 前端服务..."
    pm2 restart "$APP_NAME"
    ;;
  status)
    pm2 status
    ;;
  logs)
    pm2 logs "$APP_NAME"
    ;;
  *)
    echo "用法: $0 {start|stop|restart|status|logs}"
    exit 1
    ;;
esac

exit 0
