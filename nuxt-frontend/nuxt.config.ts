// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // 关闭服务器端渲染，生成静态SPA
  ssr: false,

  // 开发工具配置
  devtools: { enabled: true },

  // 开发服务器配置
  devServer: {
    port: 5173,
    host: '0.0.0.0'
  },

  // 启用的 Nuxt 模块
  modules: [
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss'
  ],

  // 全局引入的 CSS 文件
  css: ['~/assets/css/main.css'],

  // 应用级配置（页面头部信息）
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

  // 运行时配置（环境变量）
  runtimeConfig: {
    public: {
      // 优先级：环境变量 > 本地默认地址
      apiBaseUrl: process.env.API_BASE_URL || ''
    }
  },

  // Nitro 服务器配置（代理、路由规则）
  nitro: {
    // 获取后端API地址 - 统一配置源
    $development: {
      // 开发环境：代理所有请求到后端
      devProxy: {
        '/api/**': {
          target: process.env.API_BASE_URL || 'http://localhost:8001',
          changeOrigin: true,
          prependPath: true
        },
        '/docs/**': {
          target: process.env.API_BASE_URL || 'http://localhost:8001',
          changeOrigin: true
        },
        '/openapi.json': {
          target: process.env.API_BASE_URL || 'http://localhost:8001',
          changeOrigin: true
        }
      }
    },
    // 生产环境路由规则
    routeRules: {
      // API 接口 - 生产环境后端直接serving
      '/api/**': {
        proxy: process.env.API_BASE_URL ? `${process.env.API_BASE_URL}/api/**` : undefined
      },
      // 文档接口
      '/docs/**': {
        proxy: process.env.API_BASE_URL ? `${process.env.API_BASE_URL}/docs/**` : undefined
      },
      '/openapi.json': {
        proxy: process.env.API_BASE_URL ? `${process.env.API_BASE_URL}/openapi.json` : undefined
      }
    }
  }
})