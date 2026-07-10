import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import type { ApiError, TokenResponse } from '@/types/auth'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'
const REFRESH_TOKEN_KEY = 'aja_refresh_token'

let accessToken: string | null = null
let refreshPromise: Promise<TokenResponse> | null = null

export const tokenStorage = {
  getAccessToken: () => accessToken,
  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  setTokens(access: string, refresh: string) {
    accessToken = access
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
  },
  clear() {
    accessToken = null
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  },
}

export const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = tokenStorage.getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

async function refreshAccessToken(): Promise<TokenResponse> {
  const refreshToken = tokenStorage.getRefreshToken()
  if (!refreshToken) {
    throw new Error('No refresh token')
  }

  if (!refreshPromise) {
    refreshPromise = axios
      .post<TokenResponse>(`${baseURL}/auth/refresh`, { refresh_token: refreshToken })
      .then((response) => {
        tokenStorage.setTokens(response.data.access_token, response.data.refresh_token)
        return response.data
      })
      .finally(() => {
        refreshPromise = null
      })
  }

  return refreshPromise
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/login') &&
      !originalRequest.url?.includes('/auth/refresh')
    ) {
      originalRequest._retry = true
      try {
        const tokens = await refreshAccessToken()
        originalRequest.headers.Authorization = `Bearer ${tokens.access_token}`
        return api(originalRequest)
      } catch {
        tokenStorage.clear()
      }
    }

    return Promise.reject(error)
  },
)

export { refreshAccessToken }
