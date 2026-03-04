// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  devServer: {
    port: 5173,
    host: '0.0.0.0'
  },

  modules: [
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss'
  ],

  css: ['~/assets/css/main.css'],

  app: {
    head: {
      title: '极简广播剧系统',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: '简约高效的音频管理平台' }
      ]
    }
  },

  runtimeConfig: {
    public: {
      // 调整优先级：优先读取 Docker 容器环境变量 API_BASE_URL，其次是原有的 NUXT_PUBLIC_API_BASE_URL，最后兜底
      apiBaseUrl: process.env.API_BASE_URL || process.env.NUXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000'
    }
  },
nitro: {
             devProxy: {
                '/api': {
                  target: process.env.API_BASE_URL || 'http://backend:8000',
                  changeOrigin: true
                }
              },
             routeRules: {
              '/api/**': {
                proxy: process.env.API_BASE_URL || 'http://backend:8000/**'
              }
            }
          }
})