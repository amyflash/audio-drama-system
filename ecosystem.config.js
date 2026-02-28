module.exports = {
  apps: [{
    name: 'audio-drama-frontend',
    script: '/home/duoduo/.openclaw/workspace/audio-drama-system/start-frontend.sh',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'development'
    },
    error_file: '/tmp/pm2-frontend-error.log',
    out_file: '/tmp/pm2-frontend-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss',
    merge_logs: true,
    autorestart: true,
    max_restarts: 5,
    min_uptime: '10s'
  }]
};
