import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '../utils/request'

export interface Episode {
  id?: number
  album_id: number
  title: string
  episode_number: number
  description?: string
  audio_url: string
  duration?: number
  file_size?: number
  file_type?: string
  created_at?: string
}

export const useEpisodeStore = defineStore('episodes', () => {
  const episodes = ref<Episode[]>([])
  const currentEpisode = ref<Episode | null>(null)
  const loading = ref(false)
  const uploading = ref(false)

  // 获取专辑的所有单集
  async function fetchEpisodes(albumId: number) {
    loading.value = true
    try {
      episodes.value = await axios.get(`/api/admin/albums/${albumId}/episodes`)
    } catch (error) {
      console.error('获取单集失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取单个单集
  async function fetchEpisode(albumId: number, episodeId: number) {
    loading.value = true
    try {
      currentEpisode.value = await axios.get(`/api/admin/albums/${albumId}/episodes/${episodeId}`)
    } catch (error) {
      console.error('获取单集失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建单集
  async function createEpisode(albumId: number, episode: Omit<Episode, 'id' | 'created_at' | 'album_id'>) {
    try {
      const result = await axios.post(`/api/admin/albums/${albumId}/episodes`, {
        ...episode,
        album_id: albumId
      })
      return result
    } catch (error) {
      console.error('创建单集失败:', error)
      throw error
    }
  }

  // 上传音频文件
  async function uploadAudio(albumId: number, file: File, fileTitle?: string) {
    uploading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      if (fileTitle) {
        formData.append('title', fileTitle)
      }

      const result = await axios.post(`/api/admin/albums/${albumId}/episodes/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return result
    } catch (error) {
      console.error('上传音频失败:', error)
      throw error
    } finally {
      uploading.value = false
    }
  }

  // 批量上传
  async function batchUpload(albumId: number, files: FileList) {
    uploading.value = true
    const results = []

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        const title = file.name.replace(/\.[^/.]+$/, '') // 移除扩展名
        const result = await uploadAudio(albumId, file, title)
        results.push(result)
      }
      return results
    } catch (error) {
      console.error('批量上传失败:', error)
      throw error
    } finally {
      uploading.value = false
    }
  }

  // 更新单集
  async function updateEpisode(albumId: number, episodeId: number, data: Partial<Episode>) {
    try {
      const result = await axios.put(`/api/admin/albums/${albumId}/episodes/${episodeId}`, data)
      return result
    } catch (error) {
      console.error('更新单集失败:', error)
      throw error
    }
  }

  // 删除单集
  async function deleteEpisode(albumId: number, episodeId: number) {
    try {
      await axios.delete(`/api/admin/albums/${albumId}/episodes/${episodeId}`)
    } catch (error) {
      console.error('删除单集失败:', error)
      throw error
    }
  }

  return {
    episodes,
    currentEpisode,
    loading,
    uploading,
    fetchEpisodes,
    fetchEpisode,
    createEpisode,
    uploadAudio,
    batchUpload,
    updateEpisode,
    deleteEpisode
  }
})
