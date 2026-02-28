#!/bin/bash
# PM2 广播剧前端服务管理脚本

case "$1" in
  start)
    echo "启动音频剧前端服务..."
    pm2 start /home/duoduo/.openclaw/workspace/audio-drama-system/ecosystem.config.js
    ;;
  stop)
    echo "停止音频剧前端服务..."
    pm2 stop audio-drama-frontend
    ;;
  restart)
    echo "重启音频剧前端服务..."
    pm2 restart audio-drama-frontend
    ;;
  status)
    pm2 status
    ;;
  logs)
    pm2 logs audio-drama-frontend
    ;;
  *)
    echo "用法: $0 {start|stop|restart|status|logs}"
    exit 1
    ;;
esac

exit 0
