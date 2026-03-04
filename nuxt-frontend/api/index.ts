import axios from 'axios'

// 适配 Nuxt 3 的环境变量读取（兼容服务端/客户端）
// 优先读取容器环境变量，其次是 Nuxt 内置的环境变量，最后兜底
const getBaseUrl = () => {
  // 容器环境变量（Docker 传入）
  const dockerEnvUrl = process.env.API_BASE_URL;
  // Nuxt 公共环境变量（原逻辑）
  const nuxtPublicUrl = process.env.NUXT_PUBLIC_API_BASE_URL;
  // 兜底地址
  const fallbackUrl = 'http://127.0.0.1:8000';

  return dockerEnvUrl || nuxtPublicUrl || fallbackUrl;
};

const baseURL = getBaseUrl();

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add token
api.interceptors.request.use((config) => {
  // 在服务端不访问 localStorage
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api