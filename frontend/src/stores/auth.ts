import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi, type User } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(JSON.parse(localStorage.getItem('user') || 'null'))
  const isAuthenticated = ref<boolean>(!!token.value)
  let heartbeatInterval: number | null = null

  const setToken = (newToken: string, userData: User) => {
    token.value = newToken
    user.value = userData
    localStorage.setItem('token', newToken)
    localStorage.setItem('user', JSON.stringify(userData))
    isAuthenticated.value = true
    startHeartbeat()
  }

  const clearToken = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    isAuthenticated.value = false
    stopHeartbeat()
  }

  const login = async (username: string, password: string) => {
    const response = await authApi.login({ username, password })
    setToken(response.data.access_token, response.data.user)
    return response
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } finally {
      clearToken()
    }
  }

  const isAdmin = () => {
    return user.value?.role === 'admin'
  }

  const getUserDisplayName = () => {
    return user.value?.username || '未知用户'
  }

  const startHeartbeat = () => {
    if (heartbeatInterval) return

    // Send heartbeat every 3 minutes (server expires after 5)
    heartbeatInterval = window.setInterval(async () => {
      try {
        await authApi.heartbeat()
      } catch (error) {
        console.error('Heartbeat failed:', error)
        clearToken()
      }
    }, 3 * 60 * 1000)
  }

  const stopHeartbeat = () => {
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
      heartbeatInterval = null
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    getUserDisplayName,
    login,
    logout,
    setToken
  }
})
