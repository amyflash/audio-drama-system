import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '../utils/request'

export interface Album {
  id?: number
  title: string
  description?: string
  cover_url?: string
  author?: string
  created_at?: string
  episode_count?: number
}

export const useAlbumStore = defineStore('albums', () => {
  const albums = ref<Album[]>([])
  const currentAlbum = ref<Album | null>(null)
  const loading = ref(false)

  // 获取所有专辑
  async function fetchAlbums() {
    loading.value = true
    try {
      albums.value = await axios.get('/api/admin/albums')
    } catch (error) {
      console.error('获取专辑失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取单个专辑
  async function fetchAlbum(id: number) {
    loading.value = true
    try {
      currentAlbum.value = await axios.get(`/api/admin/albums/${id}`)
    } catch (error) {
      console.error('获取专辑失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建专辑
  async function createAlbum(data: Omit<Album, 'id' | 'created_at' | 'episode_count'>) {
    try {
      const result = await axios.post('/api/admin/albums', data)
      await fetchAlbums()
      return result
    } catch (error) {
      console.error('创建专辑失败:', error)
      throw error
    }
  }

  // 更新专辑
  async function updateAlbum(id: number, data: Partial<Album>) {
    try {
      const result = await axios.put(`/api/admin/albums/${id}`, data)
      await fetchAlbums()
      return result
    } catch (error) {
      console.error('更新专辑失败:', error)
      throw error
    }
  }

  // 删除专辑
  async function deleteAlbum(id: number) {
    try {
      await axios.delete(`/api/admin/albums/${id}`)
      await fetchAlbums()
    } catch (error) {
      console.error('删除专辑失败:', error)
      throw error
    }
  }

  return {
    albums,
    currentAlbum,
    loading,
    fetchAlbums,
    fetchAlbum,
    createAlbum,
    updateAlbum,
    deleteAlbum
  }
})
