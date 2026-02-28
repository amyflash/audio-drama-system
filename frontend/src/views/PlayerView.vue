<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 pb-8">
    <!-- 移动端顶部导航 -->
    <div class="bg-white shadow-sm border-b px-4 py-3 sticky top-0 z-50 flex items-center gap-3">
      <button
        @click="$router.back()"
        class="text-blue-600 hover:text-blue-700 px-2 py-1 text-sm font-medium transition-colors"
      >
        ← 返回
      </button>
      <span class="font-semibold text-gray-700 text-sm truncate">播放中</span>
    </div>

    <div class="max-w-4xl mx-auto p-4 sm:p-6">
      <!-- 加载状态 -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin text-4xl text-blue-500">
          <svg class="w-10 h-10" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-opacity="0.25"></circle>
            <path d="M4 12a8 8 0 018-8" stroke="currentColor" stroke-width="4" stroke-linecap="round"></path>
          </svg>
        </div>
      </div>

      <!-- 播放器内容 -->
      <div v-else-if="episode" class="bg-white rounded-xl shadow-sm p-6 sm:p-8">
        <!-- 标题区域 -->
        <div class="text-center mb-6 sm:mb-8">
          <h1 class="text-xl sm:text-3xl font-bold text-gray-800 mb-2">{{ episode.title }}</h1>
          <p class="text-gray-600 text-sm sm:text-base">第 {{ episode.sort_order + 1 }} 集</p>
        </div>

        <!-- 专辑封面/图标 -->
        <div class="bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl p-8 sm:p-12 mb-6 text-center mx-auto max-w-sm">
          <span class="text-6xl sm:text-8xl">🎧</span>
        </div>

        <!-- 音频播放器 -->
        <div class="max-w-2xl mx-auto">
          <audio
            ref="audioPlayer"
            :src="streamUrl"
            controls
            class="w-full"
            @timeupdate="handleTimeUpdate"
            @loadedmetadata="handleLoadedMetadata"
          ></audio>

          <!-- 音频信息 -->
          <div class="mt-4 sm:mt-6 space-y-1 sm:space-y-2 text-center text-gray-500 text-sm sm:text-base">
            <p>⏱️ 时长: {{ formatDuration(episode.duration) }}</p>
            <p v-if="audioInfo.size">📦 大小: {{ audioInfo.size }}</p>
            <p class="text-xs sm:text-sm">支持格式: MP3 / OGG / FLAC</p>
          </div>
        </div>

        <!-- 播放控制提示 -->
        <div class="mt-6 sm:mt-8 text-center">
          <p class="text-gray-500 text-xs sm:text-sm">
            💡 提示: 播放进度会自动保存，下次继续
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { episodeApi } from '@/api/episode'

const route = useRoute()
const episodeId = ref<number>(parseInt(route.params.id as string))

const episode = ref<any>(null)
const loading = ref(true)
const audioPlayer = ref<HTMLAudioElement | null>(null)
const audioInfo = ref({ size: '', format: '' })

const streamUrl = computed(() => episodeApi.getStreamUrl(episodeId.value))

const loadEpisode = async () => {
  try {
    const response = await episodeApi.get(episodeId.value)
    episode.value = response.data
  } catch (error) {
    console.error('加载单集失败', error)
    loading.value = false
  } finally {
    loading.value = false
  }
}

const handleTimeUpdate = () => {
  if (audioPlayer.value) {
    // 保存播放进度（每5秒保存一次，减少写入频率）
    const currentTime = Math.floor(audioPlayer.value.currentTime)
    const lastSave = parseInt(localStorage.getItem(`playback-time-${episodeId.value}`) || '0')
    if (currentTime - lastSave >= 5) {
      localStorage.setItem(`playback-pos-${episodeId.value}`, currentTime.toString())
      localStorage.setItem(`playback-time-${episodeId.value}`, Date.now().toString())
    }
  }
}

const handleLoadedMetadata = () => {
  if (audioPlayer.value) {
    // 恢复播放进度
    const savedPos = localStorage.getItem(`playback-pos-${episodeId.value}`)
    if (savedPos) {
      audioPlayer.value.currentTime = parseFloat(savedPos)
    }

    // 获取音频信息
    if (audioPlayer.value.duration) {
      audioInfo.value.size = formatDuration(audioPlayer.value.duration)
    }
  }
}

// 页面离开时保存当前位置
const saveProgressBeforeLeave = () => {
  if (audioPlayer.value) {
    localStorage.setItem(`playback-pos-${episodeId.value}`,
      Math.floor(audioPlayer.value.currentTime).toString())
  }
}

const formatDuration = (seconds: number) => {
  if (!seconds || !isFinite(seconds)) return '未知'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

onMounted(() => {
  loadEpisode()
  window.addEventListener('beforeunload', saveProgressBeforeLeave)
})

onUnmounted(() => {
  saveProgressBeforeLeave()
  window.removeEventListener('beforeunload', saveProgressBeforeLeave)
})
</script>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
