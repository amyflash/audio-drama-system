import api from './index'

export interface Episode {
  id: number
  album_id: number
  title: string
  duration: number
  sort_order: number
  created_at: string
  stream_url?: string
}

export interface EpisodeCreate {
  title: string
  sort_order?: number
}

export const episodeApi = {
  getByAlbum: (albumId: number) =>
    api.get<{items: Episode[], album_id: number}>(`/api/admin/albums/${albumId}/episodes`),

  get: (id: number) =>
    api.get<Episode>(`/api/admin/episodes/${id}`),

  upload: (id: number, file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData()
    formData.append('file', file)

    return api.post<Episode>(`/api/admin/episodes/${id}/upload`, formData, {
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

    return api.post<{success: true, uploaded: number, total: number}>(`/api/admin/albums/${albumId}/episodes/batch-upload`, formData, {
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

  create: (albumId: number, data: EpisodeCreate) =>
    api.post<Episode>(`/api/admin/albums/${albumId}/episodes`, data),

  update: (id: number, data: Partial<EpisodeCreate>) =>
    api.put<Episode>(`/api/admin/episodes/${id}`, data),

  delete: (id: number) =>
    api.delete(`/api/admin/episodes/${id}`),

  getStreamUrl: (id: number) =>
    `${api.defaults.baseURL}/api/stream/${id}`
}
