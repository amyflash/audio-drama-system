import api from './index'

export interface Album {
  id: number
  title: string
  description: string | null
  cover_image: string
  sort_order: number
  episode_count: number
  created_at: string
  updated_at: string
}

export interface AlbumCreate {
  title: string
  cover_image: string
  description?: string
  sort_order?: number
}

// 默认封面图片（简单的紫色渐变 SVG）
export const DEFAULT_COVER = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImciIHgxPSIwJSIgeTE9IjAlIiB4Mj0iMTAwJSIgeTI9IjEwMCUiPjxzdG9wIG9mZnNldD0iMCUiIHN0eWxlPSJzdG9wLWNvbG9yIiMzYfGQ3OTUiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0eWxlPSJzdG9wLWNvbG9yOiM3YzNhZWQiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0idXJsKCNnKSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0iY2VudHJhbCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0id2hpdGUiIGZvbnQtc2l6ZT0iNDBweIiBmb250LWZhbWlseT0iQXJpYWwiPuWFqOeJrzwvdGV4dD48L3N2Zz4='

export const albumApi = {
  list: () =>
    api.get<{items: Album[], total: number, page: number}>('/api/admin/albums'),

  get: (id: number) =>
    api.get<Album>(`/api/admin/albums/${id}`),

  create: (data: AlbumCreate) =>
    api.post<Album>('/api/admin/albums', {
      ...data,
      cover_image: data.cover_image || DEFAULT_COVER
    }),

  update: (id: number, data: Partial<AlbumCreate>) =>
    api.put<Album>(`/api/admin/albums/${id}`, data),

  delete: (id: number) =>
    api.delete(`/api/admin/albums/${id}`)
}
