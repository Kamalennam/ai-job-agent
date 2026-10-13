import { api } from './api'
import type { Profile, UpdateProfileRequest } from '@/types/profile'

export const profileService = {
  async get(): Promise<Profile> {
    const response = await api.get<Profile>('/users/me')
    return response.data
  },

  async update(payload: UpdateProfileRequest): Promise<Profile> {
    const response = await api.put<Profile>('/users/me', payload)
    return response.data
  },

  async uploadAvatar(file: File): Promise<Profile> {
    const body = new FormData()
    body.append('file', file)
    const response = await api.post<Profile>('/users/me/avatar', body)
    return response.data
  },

  async removeAvatar(): Promise<Profile> {
    const response = await api.delete<Profile>('/users/me/avatar')
    return response.data
  },
}
