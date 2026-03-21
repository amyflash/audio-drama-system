<template>
  <div class="min-h-screen bg-gradient-to-br from-emerald-50 via-green-50 to-emerald-100 flex items-center justify-center p-4">
    <div class="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl w-full max-w-md overflow-hidden border border-emerald-100">
      <!-- 顶部装饰：绿色护眼风 -->
      <div class="bg-gradient-to-r from-emerald-500 via-emerald-600 to-emerald-700 p-6 sm:p-8 text-center">
        <div class="text-6xl sm:text-7xl mb-3 sm:mb-4">🌿</div>
        <h1 class="text-xl sm:text-3xl font-bold text-emerald-50 mb-1 sm:mb-2">极简广播剧</h1>
        <p class="text-emerald-100/90 text-base sm:text-lg">柔和绿色 · 护眼登录</p>
      </div>

      <!-- 登录区域 -->
      <div class="p-6 sm:p-8 bg-gradient-to-b from-emerald-50/40 to-white">
        <!-- SSO 统一登录 -->
        <div v-if="!ssoLoading">
          <button
            @click="handleSSOLogin"
            :disabled="loading"
            class="w-full bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-emerald-50 font-semibold py-4 px-4 rounded-lg shadow-md shadow-emerald-200/80 transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            {{ loading ? '正在跳转...' : '统一账号登录' }}
          </button>
        </div>

        <!-- SSO 登录中 -->
        <div v-else class="text-center py-4">
          <div class="flex items-center justify-center gap-2 text-emerald-600">
            <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>正在验证登录状态...</span>
          </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {{ error }}
        </div>
      </div>

      <!-- 底部 -->
      <div class="bg-emerald-50 px-6 sm:px-8 py-3 sm:py-4 text-center text-xs text-emerald-400">
        极简广播剧系统 v1.0 · 护眼模式
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const loading = ref(false)
const ssoLoading = ref(false)
const error = ref('')

// 处理 SSO 登录跳转
const handleSSOLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await $fetch('/api/auth/sso/login-url', {
      params: {
        // FIX: 登录成功后由后端 HTML 回调页跳转到首页
        // 不能用 window.location.href（那是登录页自身），要明确指定目标页
        redirect_uri: window.location.origin + '/'
      }
    })
    window.location.href = response.login_url
  } catch (e: any) {
    error.value = '获取登录地址失败，请稍后重试'
    loading.value = false
  }
}

// FIX: 删除 handleSSOCallback
// 原来的逻辑期望 jwt-auth 把 token 带回登录页再由前端 POST 验证，
// 但实际上 jwt-auth 直接把浏览器重定向到后端 /api/auth/sso/callback，
// 由后端 HTML 页面写 localStorage 并跳转，前端这里永远拿不到 token query 参数。
// 两套流程混用导致 localStorage 始终为空。
// 现在统一由后端 HTML 回调页负责写 localStorage + 跳转，前端无需处理。

onMounted(async () => {
  // FIX: 不再在登录页处理回调，回调由后端 /api/auth/sso/callback 的 HTML 页面处理
})
</script>