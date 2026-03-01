<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 flex items-center justify-center p-4">
    <div class="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
      <!-- 顶部装饰 -->
      <div class="bg-gradient-to-r from-blue-500 to-purple-600 p-6 sm:p-8 text-center">
        <div class="text-6xl sm:text-7xl mb-3 sm:mb-4">🎭</div>
        <h1 class="text-xl sm:text-3xl font-bold text-white mb-1 sm:mb-2">极简广播剧</h1>
        <p class="text-blue-100 text-base sm:text-lg">简约高效 · 音频管理</p>
      </div>

      <!-- 登录表单 -->
      <div class="p-6 sm:p-8">
        <form @submit.prevent="handleLogin">
          <!-- 用户名输入 -->
          <div class="mb-5">
            <label class="block text-gray-700 text-base sm:text-sm font-bold mb-2">用户名</label>
            <input
              v-model="username"
              type="text"
              placeholder="请输入用户名"
              required
              class="w-full px-4 py-3 sm:py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <!-- 密码输入 -->
          <div class="mb-6">
            <label class="block text-gray-700 text-base sm:text-sm font-bold mb-2">密码</label>
            <input
              v-model="password"
              type="password"
              placeholder="请输入密码"
              required
              class="w-full px-4 py-3 sm:py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              show-password
            />
          </div>

          <!-- 登录按钮 -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 py-sm-4 px-4 rounded-lg transition-colors duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ loading ? '登录中...' : '登录' }}
          </button>

          <!-- 错误提示 -->
          <div v-if="error" class="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {{ error }}
          </div>

          <!-- 测试账号提示 -->
          <div class="mt-6 text-center text-sm sm:text-base text-gray-500 bg-gray-50 rounded-lg p-3 sm:p-4">
            <div class="font-medium mb-2">📝 测试账号</div>
            <div class="text-sm sm:text-base">用户名: <span class="font-mono bg-gray-200 px-2 py-1 rounded">admin</span></div>
            <div class="text-sm sm:text-base">密码: <span class="font-mono bg-gray-200 px-2 py-1 rounded">123456</span></div>
          </div>
        </form>
      </div>

      <!-- 底部装饰 -->
      <div class="bg-gray-50 px-6 sm:px-8 py-3 sm:py-4 text-center text-xs sm:text-xs text-gray-400">
        极简广播剧系统 v1.0 · Vue 3 + FastAPI
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from '#app'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!username.value.trim() || !password.value.trim()) {
    error.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  error.value = ''

  try {
    // 调用登录 API（在页面直接使用 auth API）
    const { $authApi } = useNuxtApp()
    const response = await $authApi.login({ username: username.value, password: password.value })
    const loginData = response.data

    // 保存 token 和用户信息
    if (process.client) {
      localStorage.setItem('token', loginData.access_token)
      localStorage.setItem('user', JSON.stringify(loginData.user))
    }

    error.value = ''
    await navigateTo('/')
  } catch (err: any) {
    error.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>
