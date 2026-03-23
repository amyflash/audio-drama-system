import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/api/auth'

export interface SSOConfig {
  ssoEnabled: boolean
  localLoginEnabled: boolean
  jwtAuthUrl: string
}

export interface SSOLoginUrl {
  loginUrl: string
  callbackUrl: string
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const ssoConfig = ref<SSOConfig | null>(null)
  const ssoLoading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const userDisplayName = computed(() => {
    if (!user.value) return ''
    if (user.value.first_name && user.value.last_name) {
      return `${user.value.first_name} ${user.value.last_name}`
    }
    return user.value.username
  })

  // 初始化 - 从 localStorage 恢复状态
  const initFromStorage = () => {
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem('token')
      const storedUser = localStorage.getItem('user')
      if (storedToken) {
        token.value = storedToken
      }
      if (storedUser) {
        try {
          user.value = JSON.parse(storedUser)
        } catch (e) {
          console.error('解析用户信息失败:', e)
        }
      }
    }
  }

  // 设置用户和令牌
  const setUser = (newUser: User, newToken: string) => {
    user.value = newUser
    token.value = newToken
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', newToken)
      localStorage.setItem('user', JSON.stringify(newUser))
    }
  }

  // 清除用户和令牌
  const clearUser = () => {
    user.value = null
    token.value = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }

  // 获取 SSO 状态
  const loadSSOStatus = async () => {
    try {
      const response = await fetch('/api/auth/sso/status')
      if (response.ok) {
        ssoConfig.value = await response.json()
      }
    } catch (error) {
      console.error('加载 SSO 状态失败:', error)
    }
    return ssoConfig.value
  }

  // 获取 SSO 登录 URL
  const getSSOLoginUrl = async (redirectUri: string): Promise<SSOLoginUrl> => {
    const params = new URLSearchParams({ redirect_uri: redirectUri })
    const response = await fetch(`/api/auth/sso/login-url?${params.toString()}`)
    if (!response.ok) {
      throw new Error('获取登录地址失败')
    }
    return response.json()
  }

  // SSO 登录跳转
  const ssoLogin = async (redirectUri?: string) => {
    ssoLoading.value = true
    try {
      const uri = redirectUri || window.location.origin + '/'
      const { loginUrl } = await getSSOLoginUrl(uri)
      window.location.href = loginUrl
    } catch (error) {
      console.error('SSO 登录失败:', error)
      throw error
    } finally {
      ssoLoading.value = false
    }
  }

  // 登出
  const logout = () => {
    clearUser()
  }

  // 初始化
  initFromStorage()

  return {
    // 状态
    user,
    token,
    ssoConfig,
    ssoLoading,
    // 计算属性
    isAuthenticated,
    isAdmin,
    userDisplayName,
    // 方法
    initFromStorage,
    setUser,
    clearUser,
    loadSSOStatus,
    getSSOLoginUrl,
    ssoLogin,
    logout
  }
})
