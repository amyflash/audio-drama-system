import api from './index'

export interface User {
  id: number
  username: string
  role: string
  is_active: boolean
  first_name?: string
  last_name?: string
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

export const login = (data: LoginRequest) =>
  api.post<LoginResponse>('/api/auth/login', data)

export const logout = () =>
  api.post('/api/auth/logout')

export const heartbeat = () =>
  api.post('/api/auth/heartbeat')

export const getCurrentUser = () =>
  api.get<User>('/api/auth/me')
