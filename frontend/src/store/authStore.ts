import { create } from 'zustand'
import { authService } from '@/services/authService'
import { refreshAccessToken, tokenStorage } from '@/services/api'
import type { RegisterRequest, RegisterResponse } from '@/types/auth'

interface AuthStore {
  accessToken: string | null
  isAuthenticated: boolean
  isInitializing: boolean
  initialize: () => Promise<void>
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterRequest) => Promise<RegisterResponse>
  verifyEmail: (token: string) => Promise<string>
  resendVerification: (email: string) => Promise<string>
  logout: () => Promise<void>
}

export const useAuthStore = create<AuthStore>((set) => ({
  accessToken: null,
  isAuthenticated: false,
  isInitializing: true,

  initialize: async () => {
    const refreshToken = tokenStorage.getRefreshToken()
    if (!refreshToken) {
      set({ isInitializing: false, isAuthenticated: false, accessToken: null })
      return
    }

    try {
      const tokens = await refreshAccessToken()
      set({
        accessToken: tokens.access_token,
        isAuthenticated: true,
        isInitializing: false,
      })
    } catch {
      tokenStorage.clear()
      set({ accessToken: null, isAuthenticated: false, isInitializing: false })
    }
  },

  login: async (email, password) => {
    const tokens = await authService.login({ email, password })
    tokenStorage.setTokens(tokens.access_token, tokens.refresh_token)
    set({ accessToken: tokens.access_token, isAuthenticated: true })
  },

  register: async (data) => {
    return authService.register(data)
  },

  verifyEmail: async (token) => {
    const response = await authService.verifyEmail(token)
    return response.message
  },

  resendVerification: async (email) => {
    const response = await authService.resendVerification(email)
    return response.message
  },

  logout: async () => {
    try {
      if (tokenStorage.getAccessToken()) {
        await authService.logout()
      }
    } finally {
      tokenStorage.clear()
      set({ accessToken: null, isAuthenticated: false })
    }
  },
}))
