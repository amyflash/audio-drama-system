import { defineNuxtPlugin } from '#app'
import axios from 'axios'

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()

  // 创建共享的 axios 实例
  const api = axios.create({
    baseURL: config.public.apiBaseUrl,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  // Request interceptor to add token
  api.interceptors.request.use((config) => {
    // 在服务端不访问 localStorage
    if (import.meta.client) {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  })

  // Response interceptor for error handling
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401 && import.meta.client) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }
  )

  // Auth API
  const authApi = {
    login: (data: {username: string, password: string}) =>
      api.post('/api/auth/login', data),
    logout: () =>
      api.post('/api/auth/logout'),
    heartbeat: () =>
      api.post('/api/auth/heartbeat'),
    getCurrentUser: () =>
      api.get('/api/auth/me'),
    getUsers: () =>
      api.get('/api/admin/users'),
    createUser: (data: any) =>
      api.post('/api/admin/users', data),
    updateUser: (id: number, data: any) =>
      api.put(`/api/admin/users/${id}`, data),
    deleteUser: (id: number) =>
      api.delete(`/api/admin/users/${id}`)
  }

  // Album API
  const DEFAULT_COVER = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImciIHgxPSIwJSIgeTE9IjAlIiB4Mj0iMTAwJSIgeTI9IjEwMCUiPjxzdG9wIG9mZnNldD0iMCUiIHN0eWxlPSJzdG9wLWNvbG9yIiMzYfGQ3OTUiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0eWxlPSJzdG9wLWNvbG9yOiM3YzNhZWQiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0idXJsKCNnKSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0iY2VudHJhbCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0id2hpdGUiIGZvbnQtc2l6ZT0iNDBweCIgZm9udC1mYW1pbHk9IkFyaWFsIj7lha3lia88L3RleHQ+PC9zdmc+'

  const albumApi = {
    list: () =>
      api.get<{items: any[], total: number, page: number}>('/api/admin/albums'),
    get: (id: number) =>
      api.get(`/api/admin/albums/${id}`),
    create: (data: any) =>
      api.post('/api/admin/albums', data),
    update: (id: number, data: any) =>
      api.put(`/api/admin/albums/${id}`, data),
    delete: (id: number) =>
      api.delete(`/api/admin/albums/${id}`)
  }

  // Episode API
  const episodeApi = {
    getByAlbum: (albumId: number) =>
      api.get(`/api/admin/albums/${albumId}/episodes`),
    get: (id: number) =>
      api.get(`/api/admin/episodes/${id}`),
    upload: (id: number, file: File, onProgress?: (progress: number) => void) => {
      const formData = new FormData()
      formData.append('file', file)

      return api.post(`/api/admin/episodes/${id}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            onProgress(progress)
          }
        }
      })
    },
    batchUpload: (albumId: number, files: File[], onProgress?: (progress: number) => void) => {
      const formData = new FormData()
      files.forEach((file) => {
        formData.append('files', file)
      })

      return api.post(`/api/admin/albums/${albumId}/episodes/batch-upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            onProgress(progress)
          }
        }
      })
    },
    create: (albumId: number, data: any) =>
      api.post(`/api/admin/albums/${albumId}/episodes`, data),
    update: (id: number, data: any) =>
      api.put(`/api/admin/episodes/${id}`, data),
    delete: (id: number) =>
      api.delete(`/api/admin/episodes/${id}`)
  }

  // 为 episodeApi 添加 getStreamUrl 方法
  episodeApi.getStreamUrl = (id: number) =>
    `${config.public.apiBaseUrl}/api/stream/${id}` as any

  // 提供 API 方法
  return {
    provide: {
      authApi,
      albumApi,
      episodeApi
    }
  }
})
