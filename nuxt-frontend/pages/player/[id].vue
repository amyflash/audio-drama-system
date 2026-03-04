<template>
  <div class="min-h-screen bg-gradient-to-br from-green-900 via-green-950 to-black pb-8">
    <!-- 移动端顶部导航 -->
    <div class="bg-green-900/60 backdrop-blur-md shadow-lg border-b border-green-800/50 px-4 py-3 sticky top-0 z-50 flex items-center gap-3">
      <button
        @click="navigateTo(`/albums/${episode.album_id}`)"
        class="text-green-300 hover:text-green-200 px-2 py-1 text-sm font-medium transition-colors"
      >
        ← 返回
      </button>
      <span class="font-semibold text-green-50 text-sm truncate">播放中</span>
    </div>

    <div class="max-w-4xl mx-auto p-4 sm:p-6">
      <!-- 加载状态 -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin text-4xl text-green-400">
          <svg class="w-10 h-10" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-opacity="0.25"></circle>
            <path d="M4 12a8 8 0 018-8" stroke="currentColor" stroke-width="4" stroke-linecap="round"></path>
          </svg>
        </div>
      </div>

      <!-- 播放器内容 -->
      <div v-else-if="episode" class="bg-green-900/40 backdrop-blur-sm rounded-2xl shadow-2xl p-6 sm:p-8 border border-green-800/50">
        <!-- 标题区域 -->
        <div class="text-center mb-6 sm:mb-8">
          <h1 class="text-xl sm:text-3xl font-bold text-green-50 mb-2">{{ episode.title }}</h1>
          <p class="text-green-200/70 text-sm sm:text-base">第 {{ episode.sort_order + 1 }} 集</p>
        </div>

        <!-- 空剧集提示 -->
        <div v-if="!streamUrl || episode.duration === 0" class="bg-green-950/40 border border-green-800/50 rounded-xl p-6 sm:p-8 text-center mb-6">
          <span class="text-4xl sm:text-5xl mb-4 block">📭</span>
          <h3 class="text-lg sm:text-xl font-semibold text-green-300 mb-2">暂无音频文件</h3>
          <p class="text-green-200/70 text-sm sm:text-base mb-4">该剧集还未上传音频文件</p>
          <button
            @click="navigateTo(`/albums/${episode.album_id}`)"
            class="inline-block bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-green-50 px-6 py-2 rounded-lg text-sm font-medium transition-all shadow-lg"
          >
            上传音频文件
          </button>
        </div>

        <!-- 专辑封面/图标 -->
        <div class="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-8 sm:p-12 mb-6 text-center mx-auto max-w-sm">
          <span class="text-6xl sm:text-8xl">🎧</span>
        </div>

        <!-- 音频播放器（仅在有音频文件时显示） -->
        <div v-if="episode && !!streamUrl && episode.duration > 0" class="max-w-2xl mx-auto">
          <!-- 原生 audio 元素（提供完整控制） -->
          <audio
            ref="audioPlayer"
            :src="streamUrl"
            class="w-full"
            @timeupdate="handleTimeUpdate"
            @progress="calculateBuffered"
            @loadedmetadata="handleLoadedMetadata"
            style="display: none;"
          ></audio>

          <!-- 自定义播放控制 -->
          <div class="bg-green-950/50 backdrop-blur-sm rounded-2xl p-4 sm:p-6 border border-green-800/50">
            <!-- 进度条区域 -->
            <div class="mb-4">
              <!-- 时间显示 -->
              <div class="flex justify-between items-center mb-2 text-green-50">
                <span class="text-lg font-mono">{{ formatTime(currentTime) }}</span>
                <span class="text-lg font-mono text-green-200/70">/ {{ formatTime(duration) }}</span>
              </div>

              <!-- 进度条 -->
              <div
                class="w-full h-2 bg-green-800/60 rounded-full cursor-pointer hover:bg-green-700/60 transition-colors relative"
                @click="handleProgressClick"
              >
                <!-- 缓冲进度条（灰色） -->
                <div
                  class="absolute top-0 left-0 h-full bg-gray-500 rounded-full"
                  :style="{ width: bufferedPercentage + '%' }"
                ></div>

                <!-- 已播放进度 -->
                <div
                  class="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full relative"
                  :style="{ width: progressPercentage + '%' }"
                >
                  <!-- 进度指示点 -->
                  <div
                    class="absolute right-0 top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-lg"
                  ></div>
                </div>
              </div>
              <p class="text-green-300/50 text-xs mt-2">
                💡 点击进度条可跳转到指定位置 · 灰色为已缓冲部分
              </p>
            </div>

            <!-- 播放控制按钮 -->
            <div class="flex justify-center items-center gap-6">
              <!-- 后退 10 秒 -->
              <button
                @click="seekBy(-10)"
                class="w-12 h-12 rounded-full bg-green-800 hover:bg-green-700 text-green-50 flex items-center justify-center transition-colors shadow-lg hover:shadow-xl"
              >
                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.333 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z" />
                </svg>
              </button>

              <!-- 播放/暂停按钮 -->
              <button
                @click="togglePlay"
                class="w-16 h-16 rounded-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-green-50 flex items-center justify-center transition-all shadow-xl hover:shadow-2xl transform hover:scale-105"
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
                class="w-12 h-12 rounded-full bg-green-800 hover:bg-green-700 text-green-50 flex items-center justify-center transition-colors shadow-lg hover:shadow-xl"
              >
                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.933 12.8a1 1 0 000-1.6L6.6 7.2A1 1 0 005 8v8a1 1 0 001.6.8l5.333-4zM19.933 12.8a1 1 0 000-1.6l-5.333-4A1 1 0 0013 8v8a1 1 0 001.6.8l5.333-4z" />
                </svg>
              </button>
            </div>
          </div>

          <!-- 音频信息（仅在有音频文件时显示） -->
          <div v-if="episode.duration > 0" class="mt-4 sm:mt-6 space-y-1 sm:space-y-2 text-center text-green-200/70 text-sm sm:text-base">
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

const route = useRoute()
const { $episodeApi } = useNuxtApp()

const episodeId = ref<number>(parseInt(route.params.id as string))

const episode = ref<any>(null)
const loading = ref(true)
const audioPlayer = ref<HTMLAudioElement | null>(null)
const currentTime = ref(0)
const duration = ref(0)
const isPlaying = ref(false)
const bufferedPercentage = ref(0)

const streamUrl = ref<string>('')

const progressPercentage = computed(() => {
  if (!duration.value || !currentTime.value) return 0
  return (currentTime.value / duration.value) * 100
})

// 获取播放 token
const loadStreamUrl = async () => {
  if (episodeId.value) {
    try {
      const token = localStorage.getItem('token')
      if (token) {
        // 使用 stream token 接口获取临时播放 token
        const response = await fetch(
          `${useRuntimeConfig().public.apiBaseUrl}/api/stream/token/${episodeId.value}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        )
        const data = await response.json()
        if (data.success && data.token) {
          // 添加 token 参数到 stream URL
          streamUrl.value = `${$episodeApi.getStreamUrl(episodeId.value)}?token=${data.token}`;
        } else {
          // 失败时尝试直接使用（可能需要登录）
          streamUrl.value = $episodeApi.getStreamUrl(episodeId.value)
        }
      } else {
        // 没有登录
        streamUrl.value = $episodeApi.getStreamUrl(episodeId.value)
      }
    } catch (error) {
      console.error('获取 stream token 失败', error)
      streamUrl.value = $episodeApi.getStreamUrl(episodeId.value)
    }
  }
}

// 计算缓冲百分比
const calculateBuffered = () => {
  if (!audioPlayer.value || !duration.value) {
    bufferedPercentage.value = 0
    return
  }

  const buffered = audioPlayer.value.buffered
  if (buffered.length === 0) {
    bufferedPercentage.value = 0
    return
  }

  // 获取已缓冲的最大时间
  let bufferedEnd = 0
  for (let i = 0; i < buffered.length; i++) {
    if (buffered.end(i) > bufferedEnd) {
      bufferedEnd = buffered.end(i)
    }
  }

  bufferedPercentage.value = (bufferedEnd / duration.value) * 100
}

const loadEpisode = async () => {
  try {
    const response = await $episodeApi.get(episodeId.value)
    episode.value = response.data
    // 加载 stream URL
    await loadStreamUrl()
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
    // 计算缓冲进度
    calculateBuffered()
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

    // 计算缓冲进度
    calculateBuffered()

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
    audioPlayer.value.addEventListener('progress', calculateBuffered)
  }
})

onUnmounted(() => {
  saveProgressBeforeLeave()
  window.removeEventListener('beforeunload', saveProgressBeforeLeave)

  if (audioPlayer.value) {
    audioPlayer.value.removeEventListener('play', handlePlay)
    audioPlayer.value.removeEventListener('pause', handlePause)
    audioPlayer.value.removeEventListener('progress', calculateBuffered)
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
