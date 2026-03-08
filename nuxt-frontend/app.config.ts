// https://nuxt.com/docs/guide/directory-structure/app-config
export default defineAppConfig({
  // API 基础地址 - 构建时设置
  apiBaseUrl: process.env.API_BASE_URL || process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
})
