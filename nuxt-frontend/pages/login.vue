<template>
  <div class="min-h-screen bg-gradient-to-br from-emerald-50 via-green-50 to-emerald-100 flex items-center justify-center p-4">
    <div class="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl w-full max-w-md overflow-hidden border border-emerald-100">
      <!-- 顶部装饰：绿色护眼风 -->
      <div class="bg-gradient-to-r from-emerald-500 via-emerald-600 to-emerald-700 p-6 sm:p-8 text-center">
        <div class="text-6xl sm:text-7xl mb-3 sm:mb-4">🌿</div>
        <h1 class="text-xl sm:text-3xl font-bold text-emerald-50 mb-1 sm:mb-2">极简广播剧</h1>
        <p class="text-emerald-100/90 text-base sm:text-lg">柔和绿色 · 护眼登录</p>
      </div>

      <!-- 登录表单 -->
      <div class="p-6 sm:p-8 bg-gradient-to-b from-emerald-50/40 to-white">
        <form @submit.prevent="handleLogin">
          <!-- 用户名输入 -->
          <div class="mb-5">
            <label class="block text-emerald-900 text-base sm:text-sm font-semibold mb-2">用户名</label>
            <input
              v-model="username"
              type="text"
              placeholder="请输入用户名"
              required
              class="w-full px-4 py-3 sm:py-2 border border-emerald-200 rounded-lg bg-emerald-50/40 text-emerald-900 placeholder:text-emerald-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-shadow"
            />
          </div>

          <!-- 密码输入 -->
          <div class="mb-6">
            <label class="block text-emerald-900 text-base sm:text-sm font-semibold mb-2">密码</label>
            <input
              v-model="password"
              type="password"
              placeholder="请输入密码"
              required
              class="w-full px-4 py-3 sm:py-2 border border-emerald-200 rounded-lg bg-emerald-50/40 text-emerald-900 placeholder:text-emerald-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-shadow"
              show-password
            />
          </div>

          <!-- 登录按钮 -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-emerald-600 hover:bg-emerald-700 text-emerald-50 font-semibold py-3 px-4 rounded-lg shadow-md shadow-emerald-200/80 transition-colors duration-150 disabled:bg-emerald-300 disabled:cursor-not-allowed"
          >
            {{ loading ? '登录中...' : '登录' }}
          </button>

          <!-- 错误提示 -->
          <div v-if="error" class="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {{ error }}
          </div>

        </form>
      </div>

      <!-- 底部装饰 -->
      <div class="bg-emerald-50 px-6 sm:px-8 py-3 sm:py-4 text-center text-xs sm:text-xs text-emerald-400">
        极简广播剧系统 v1.0 · 护眼模式
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
