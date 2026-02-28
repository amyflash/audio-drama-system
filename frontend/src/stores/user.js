import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '../utils/request'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  // 登录
  async function login(username, password) {
    const data = await axios.post('/api/auth/login', {
      username,
      password
    })

    token.value = data.access_token
    user.value = data.user

    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))

    return data
  }

  // 登出
  async function logout() {
    try {
      await axios.post('/api/auth/logout')
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      token.value = ''
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }

  // 心跳保活
  async function heartbeat() {
    try {
      await axios.post('/api/auth/heartbeat')
    } catch (error) {
      console.error('心跳失败:', error)
    }
  }

  return { token, user, login, logout, heartbeat }
})
