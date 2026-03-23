export interface User {
  id: number
  username: string
  role: string
  is_active: boolean
  first_name?: string
  last_name?: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface SSOConfig {
  sso_enabled: boolean
  local_login_enabled: boolean
  jwt_auth_url: string
}

export interface SSOLoginUrl {
  login_url: string
  callback_url: string
}
