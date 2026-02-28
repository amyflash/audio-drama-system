<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-950 to-black pb-8">
    <!-- 移动端顶部导航 -->
    <div class="bg-gray-900/80 backdrop-blur-sm shadow-lg border-b border-gray-800 px-4 py-3 sticky top-0 z-50 flex items-center gap-3">
      <button
        @click="$router.back()"
        class="text-blue-400 hover:text-blue-300 px-2 py-1 text-sm font-medium transition-colors"
      >
        ← 返回
      </button>
      <span class="font-semibold text-gray-200 text-sm truncate">播放中</span>
    </div>

    <div class="max-w-4xl mx-auto p-4 sm:p-6">
      <!-- 加载状态 -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin text-4xl text-blue-400">
          <svg class="w-10 h-10" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-opacity="0.25"></circle>
            <path d="M4 12a8 8 0 018-8" stroke="currentColor" stroke-width="4" stroke-linecap="round"></path>
          </svg>
        </div>
      </div>

      <!-- 播放器内容 -->
      <div v-else-if="episode" class="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-2xl p-6 sm:p-8 border border-gray-800">
        <!-- 标题区域 -->
        <div class="text-center mb-6 sm:mb-8">
          <h1 class="text-xl sm:text-3xl font-bold text-white mb-2">{{ episode.title }}</h1>
          <p class="text-gray-400 text-sm sm:text-base">第 {{ episode.sort_order + 1 }} 集</p>
        </div>

        <!-- 空剧集提示 -->
        <div v-if="!episode.stream_url || episode.duration === 0" class="bg-gray-800/50 border border-gray-700 rounded-xl p-6 sm:p-8 text-center mb-6">
          <span class="text-4xl sm:text-5xl mb-4 block">📭</span>
          <h3 class="text-lg sm:text-xl font-semibold text-yellow-400 mb-2">暂无音频文件</h3>
          <p class="text-gray-400 text-sm sm:text-base mb-4">该剧集还未上传音频文件</p>
          <button
            @click="$router.push(`/albums/${episode.album_id}`)"
            class="inline-block bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white px-6 py-2 rounded-lg text-sm font-medium transition-all shadow-lg"
          >
            上传音频文件
          </button>
        </div>

        <!-- 专辑封面/图标 -->
        <div class="bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl p-8 sm:p-12 mb-6 text-center mx-auto max-w-sm">
          <span class="text-6xl sm:text-8xl">🎧</span>
        </div>

        <!-- 音频播放器（仅在有音频文件时显示） -->
        <div v-if="episode.stream_url && episode.duration > 0" class="max-w-2xl mx-auto">
          <!-- 原生 audio 元素（提供完整控制） -->
          <audio
            ref="audioPlayer"
            :src="streamUrl"
            class="w-full"
            @timeupdate="handleTimeUpdate"
            @loadedmetadata="handleLoadedMetadata"
            style="display: none;"
          ></audio>

          <!-- 自定义播放控制 -->
          <div class="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-4 sm:p-6 border border-gray-700">
            <!-- 进度条区域 -->
            <div class="mb-4">
              <!-- 时间显示 -->
              <div class="flex justify-between items-center mb-2 text-white">
                <span class="text-lg font-mono">{{ formatTime(currentTime) }}</span>
                <span class="text-lg font-mono text-gray-400">/ {{ formatTime(duration) }}</span>
              </div>

              <!-- 进度条 -->
              <div
                class="w-full h-2 bg-gray-700 rounded-full cursor-pointer hover:bg-gray-600 transition-colors relative"
                @click="handleProgressClick"
              >
                <!-- 已播放进度 -->
                <div
                  class="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full relative"
                  :style="{ width: progressPercentage + '%' }"
                >
                  <!-- 进度指示点 -->
                  <div
                    class="absolute right-0 top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-lg"
                  ></div>
                </div>
              </div>
              <p class="text-gray-500 text-xs mt-2">
                💡 点击进度条可跳转到指定位置
              </p>
            </div>

            <!-- 播放控制按钮 -->
            <div class="flex justify-center items-center gap-6">
              <!-- 后退 10 秒 -->
              <button
                @click="seekBy(-10)"
                class="w-12 h-12 rounded-full bg-gray-700 hover:bg-gray-600 text-white flex items-center justify-center transition-colors shadow-lg hover:shadow-xl"
              >
                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.333 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z" />
                </svg>
              </button>

              <!-- 播放/暂停按钮 -->
              <button
                @click="togglePlay"
                class="w-16 h-16 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white flex items-center justify-center transition-all shadow-xl hover:shadow-2xl transform hover:scale-105"
              >
                <svg v-if="!isPlaying" class="w-8 h-8 ml-1" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z" />
                </svg>
                <svg v-else class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
                </svg>
              </button>

              <!-- 前进 10 秒 -->
              <button
                @click="seekBy(10)"
                class="w-12 h-12 rounded-full bg-gray-700 hover:bg-gray-600 text-white flex items-center justify-center transition-colors shadow-lg hover:shadow-xl"
              >
                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.933 12.8a1 1 0 000-1.6L6.6 7.2A1 1 0 005 8v8a1 1 0 001.6.8l5.333-4zM19.933 12.8a1 1 0 000-1.6l-5.333-4A1 1 0 0013 8v8a1 1 0 001.6.8l5.333-4z" />
                </svg>
              </button>
            </div>
          </div>

          <!-- 音频信息（仅在有音频文件时显示） -->
          <div v-if="episode.duration > 0" class="mt-4 sm:mt-6 space-y-1 sm:space-y-2 text-center text-gray-400 text-sm sm:text-base">
            <p>⏱️ 总时长: {{ formatDuration(episode.duration) }}</p>
            <p class="text-xs sm:text-sm">支持格式: MP3 / OGG / FLAC</p>
          </div>
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
const currentTime = ref(0)
const duration = ref(0)
const isPlaying = ref(false)

const streamUrl = computed(() => episodeApi.getStreamUrl(episodeId.value))

const progressPercentage = computed(() => {
  if (!duration.value || !currentTime.value) return 0
  return (currentTime.value / duration.value) * 100
})

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
    currentTime.value = audioPlayer.value.currentTime
    // 保存播放进度（每5秒保存一次，减少写入频率）
    const saveTime = Math.floor(currentTime.value)
    const lastSave = parseInt(localStorage.getItem(`playback-time-${episodeId.value}`) || '0')
    if (saveTime - lastSave >= 5) {
      localStorage.setItem(`playback-pos-${episodeId.value}`, saveTime.toString())
      localStorage.setItem(`playback-time-${episodeId.value}`, Date.now().toString())
    }
  }
}

const handleLoadedMetadata = () => {
  if (audioPlayer.value) {
    duration.value = audioPlayer.value.duration

    // 恢复播放进度
    const savedPos = localStorage.getItem(`playback-pos-${episodeId.value}`)
    if (savedPos) {
      audioPlayer.value.currentTime = parseFloat(savedPos)
      currentTime.value = parseFloat(savedPos)
    }
  }
}

const togglePlay = () => {
  if (!audioPlayer.value) return

  if (isPlaying.value) {
    audioPlayer.value.pause()
  } else {
    audioPlayer.value.play()
  }
  isPlaying.value = !isPlaying.value
}

const seekBy = (seconds: number) => {
  if (!audioPlayer.value) return
  const newTime = Math.max(0, Math.min(audioPlayer.value.currentTime + seconds, audioPlayer.value.duration))
  audioPlayer.value.currentTime = newTime
}

const handleProgressClick = (event: MouseEvent) => {
  if (!audioPlayer.value) return
  const progressBar = event.currentTarget as HTMLElement
  const rect = progressBar.getBoundingClientRect()
  const clickPosition = event.clientX - rect.left
  const percentage = clickPosition / rect.width
  const newTime = percentage * audioPlayer.value.duration
  audioPlayer.value.currentTime = newTime
}

// 页面离开时保存当前位置
const saveProgressBeforeLeave = () => {
  if (audioPlayer.value) {
    localStorage.setItem(`playback-pos-${episodeId.value}`,
      Math.floor(audioPlayer.value.currentTime).toString())
  }
}

const formatTime = (seconds: number) => {
  if (!seconds || !isFinite(seconds)) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const formatDuration = (seconds: number) => {
  if (!seconds || !isFinite(seconds)) return '未知'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}分${secs}秒`
}

// 监听播放状态
const handlePlay = () => {
  isPlaying.value = true
}

const handlePause = () => {
  isPlaying.value = false
}

onMounted(() => {
  loadEpisode()
  window.addEventListener('beforeunload', saveProgressBeforeLeave)

  // 监听音频播放状态
  if (audioPlayer.value) {
    audioPlayer.value.addEventListener('play', handlePlay)
    audioPlayer.value.addEventListener('pause', handlePause)
  }
})

onUnmounted(() => {
  saveProgressBeforeLeave()
  window.removeEventListener('beforeunload', saveProgressBeforeLeave)

  if (audioPlayer.value) {
    audioPlayer.value.removeEventListener('play', handlePlay)
    audioPlayer.value.removeEventListener('pause', handlePause)
    audioPlayer.value.pause()
  }
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
