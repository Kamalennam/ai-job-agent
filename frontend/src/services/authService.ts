import { api } from './api'
import type {
  LoginRequest,
  MessageResponse,
  RegisterRequest,
  RegisterResponse,
  TokenResponse,
} from '@/types/auth'

const verifyEmailRequests = new Map<string, Promise<MessageResponse>>()

export const authService = {
  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await api.post<RegisterResponse>('/auth/register', data)
    return response.data
  },

  async verifyEmail(token: string): Promise<MessageResponse> {
    let pending = verifyEmailRequests.get(token)
    if (!pending) {
      pending = api
        .post<MessageResponse>('/auth/verify-email', { token })
        .then((response) => response.data)
      verifyEmailRequests.set(token, pending)
    }
    return pending
  },

  async resendVerification(email: string): Promise<MessageResponse> {
    const response = await api.post<MessageResponse>('/auth/resend-verification', { email })
    return response.data
  },

  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/login', data)
    return response.data
  },

  async refresh(refreshToken: string): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  async logout(): Promise<MessageResponse> {
    const response = await api.post<MessageResponse>('/auth/logout')
    return response.data
  },
}
