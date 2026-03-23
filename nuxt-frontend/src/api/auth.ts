import api from './index'
import type { User, LoginResponse, SSOConfig, SSOLoginUrl } from './types'

// SSO 状态
export const getSSOStatus = () =>
  api.get<SSOConfig>('/api/auth/sso/status')

// 获取 SSO 登录 URL
export const getSSOLoginUrl = (redirectUri: string) =>
  api.get<SSOLoginUrl>('/api/auth/sso/login-url', {
    params: { redirect_uri: redirectUri }
  })

export type { User, LoginResponse }
