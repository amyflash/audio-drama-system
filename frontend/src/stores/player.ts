import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Episode } from './episodes'

export const usePlayerStore = defineStore('player', () => {
  const currentEpisode = ref<Episode | null>(null)
  const isPlaying = ref(false)
  const currentTime = ref(0)
  const duration = ref(0)
  const audioElement = ref<HTMLAudioElement | null>(null)

  // 初始化音频元素
  function initAudio() {
    if (!audioElement.value) {
      audioElement.value = new Audio()
      audioElement.value.crossOrigin = 'anonymous'
    }
  }

  // 加载单集
  async function loadEpisode(episode: Episode) {
    initAudio()
    if (audioElement.value) {
      audioElement.value.src = episode.audio_url
      currentEpisode.value = episode
      currentTime.value = 0
      isPlaying.value = false
    }
  }

  // 播放
  function play() {
    if (audioElement.value) {
      audioElement.value.play()
      isPlaying.value = true
    }
  }

  // 暂停
  function pause() {
    if (audioElement.value) {
      audioElement.value.pause()
      isPlaying.value = false
    }
  }

  // 切换播放/暂停
  function toggle() {
    if (isPlaying.value) {
      pause()
    } else {
      play()
    }
  }

  // 跳转时间
  function seek(time: number) {
    if (audioElement.value) {
      audioElement.value.currentTime = time
      currentTime.value = time
    }
  }

  // 设置音量
  function setVolume(volume: number) {
    if (audioElement.value) {
      audioElement.value.volume = volume
    }
  }

  // 上一集
  function previous() {
    // 实现在外面，具体取决于如何管理上一集列表
  }

  // 下一集
  function next() {
    // 实现在外面，具体取决于如何管理下一集列表
  }

  // 监听原生音频事件
  function setupEventListeners(audio: HTMLAudioElement) {
    audio.addEventListener('timeupdate', () => {
      currentTime.value = audio.currentTime
    })

    audio.addEventListener('loadedmetadata', () => {
      duration.value = audio.duration
    })

    audio.addEventListener('play', () => {
      isPlaying.value = true
    })

    audio.addEventListener('pause', () => {
      isPlaying.value = false
    })

    audio.addEventListener('ended', () => {
      isPlaying.value = false
      currentTime.value = 0
    })
  }

  // 格式化时间
  function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  return {
    currentEpisode,
    isPlaying,
    currentTime,
    duration,
    audioElement,
    loadEpisode,
    play,
    pause,
    toggle,
    seek,
    setVolume,
    previous,
    next,
    setupEventListeners,
    formatTime
  }
})
