import axios from 'axios'

/**
 * API 客户端配置
 * 
 * 开发环境: 使用相对路径，Nuxt代理转发到后端 (无跨域)
 * 生产环境: 使用相对路径，后端直接serving (同域)
 */
const baseURL = ""

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 30000,  // 30秒超时
  withCredentials: true  // 允许跨域时发送cookies
})

/**
 * 请求拦截器 - 添加认证令牌
 */
api.interceptors.request.use(
  (config) => {
    // 客户端才能访问 localStorage (避免SSR错误)
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    
    // 调试日志 (仅开发环境)
    if (process.env.NODE_ENV === 'development') {
      console.debug(`[API] ${config.method?.toUpperCase()} ${config.url}`)
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

/**
 * 响应拦截器 - 全局错误处理
 */
api.interceptors.response.use(
  (response) => {
    // 调试日志 (仅开发环境)
    if (process.env.NODE_ENV === 'development') {
      console.debug(`[API] Response: ${response.status}`)
    }
    return response
  },
  (error) => {
    // 401 未授权 - 清除令牌并重定向登录
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        // 使用Nuxt路由而不是直接location.href
        window.location.href = '/login'
      }
    }
    
    // 错误日志
    console.error(`[API] Error: ${error.response?.status} - ${error.message}`)
    
    return Promise.reject(error)
  }
)

export default api