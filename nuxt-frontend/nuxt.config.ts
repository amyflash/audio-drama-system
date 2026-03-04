// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
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
      // 优先级：Docker 环境变量 > Nuxt 环境变量 > 本地默认地址
      apiBaseUrl: process.env.API_BASE_URL || process.env.NUXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000'
    }
  },

  // Nitro 服务器配置（代理、路由规则）
  nitro: {
    // 开发环境代理（仅开发模式生效）
    devProxy: {
      // 代理 OpenAPI 文档请求
      '/openapi.json': {
        target: process.env.API_BASE_URL || 'http://backend:8000',
        changeOrigin: true,
        prependPath: true
      },
      // 代理 Swagger 文档页面
      '/docs': {
        target: process.env.API_BASE_URL || 'http://backend:8000',
        changeOrigin: true,
        prependPath: true
      },
      // 代理所有 API 请求
      '/api': {
        target: process.env.API_BASE_URL || 'http://backend:8000',
        changeOrigin: true,
        prependPath: true
      }
    },
    // 通用路由规则（开发/生产环境均生效）
    routeRules: {
      // API 接口代理规则
      '/api/**': {
        proxy: `${process.env.API_BASE_URL || 'http://backend:8000'}/**`
      },
      // OpenAPI 文档代理规则
      '/openapi.json': {
        proxy: `${process.env.API_BASE_URL || 'http://backend:8000'}/openapi.json`
      },
      // 文档页面代理规则
      '/docs/**': {
        proxy: `${process.env.API_BASE_URL || 'http://backend:8000'}/docs/**`
      }
    }
  }
})