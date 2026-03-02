module.exports = {
  apps: [{
    name: 'audio-drama-nuxt',
    script: '/home/duoduo/.openclaw/workspace/audio-drama-system/start-nuxt.sh',
    instances: 1,
    exec_mode: 'fork',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'development',
      PORT: '5173'
    },
    error_file: '/tmp/pm2-nuxt-error.log',
    out_file: '/tmp/pm2-nuxt-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss',
    merge_logs: true,
    autorestart: true,
    max_restarts: 5,
    min_uptime: '10s'
  }]
};
