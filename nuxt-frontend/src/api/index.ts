import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios'
import { useUserStore } from '@/stores/user'

/**
 * API 客户端配置
 *
 * 开发环境：使用相对路径，Vite 代理转发到后端 (无跨域)
 * 生产环境：使用相对路径，后端直接 serving (同域)
 */
const api: AxiosInstance = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 30000,
  withCredentials: true
})

/**
 * 请求拦截器 - 添加认证令牌
 */
api.interceptors.request.use(
  (config) => {
    // 客户端才能访问 localStorage
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }

      // SSO 客户端需要从查询参数获取用户信息
      const userStr = localStorage.getItem('user')
      if (userStr) {
        try {
          const user = JSON.parse(userStr)
          // 将用户信息添加到查询参数
          config.params = config.params || {}
          config.params.id = user.id
          config.params.username = user.username
          config.params.role = user.role
        } catch (e) {
          console.error('解析用户信息失败:', e)
        }
      }
    }

    // 调试日志 (仅开发环境)
    if (import.meta.env.DEV) {
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
    if (import.meta.env.DEV) {
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
        // 使用路由跳转而不是直接 location.href
        window.location.href = '/login'
      }
    }

    // 错误日志
    console.error(`[API] Error: ${error.response?.status} - ${error.message}`)

    return Promise.reject(error)
  }
)

export default api
