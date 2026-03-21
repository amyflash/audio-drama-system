import api from './index'

export interface User {
  id: number
  username: string
  role: string
  is_active: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

// SSO 登录回调
export const ssoCallback = (token: string, redirectUri: string = '/') =>
  api.post<LoginResponse>('/api/auth/sso/callback', { token, redirect_uri: redirectUri })

// SSO 状态
export const getSSOStatus = () =>
  api.get<{ sso_enabled: boolean; local_login_enabled: boolean; jwt_auth_url: string }>('/api/auth/sso/status')

// 获取 SSO 登录 URL
export const getSSOLoginUrl = (redirectUri: string) =>
  api.get<{ login_url: string; callback_url: string }>('/api/auth/sso/login-url', {
    params: { redirect_uri: redirectUri }
  })
