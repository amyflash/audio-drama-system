import api from './index'

export interface User {
  id: number
  username: string
  role: string
  is_active: boolean
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export const authApi = {
  login: (data: LoginRequest) =>
    api.post<LoginResponse>('/api/auth/login', data),

  logout: () =>
    api.post('/api/auth/logout'),

  heartbeat: () =>
    api.post('/api/auth/heartbeat'),

  getCurrentUser: () =>
    api.get<User>('/api/auth/me')
}
