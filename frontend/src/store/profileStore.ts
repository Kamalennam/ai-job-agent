import { create } from 'zustand'
import { profileService } from '@/services/profileService'
import { showApiErrorToast } from '@/utils/apiError'
import type { Profile, UpdateProfileRequest } from '@/types/profile'

interface ProfileStore {
  profile: Profile | null
  isLoading: boolean
  load: () => Promise<void>
  save: (payload: UpdateProfileRequest) => Promise<Profile>
  uploadAvatar: (file: File) => Promise<Profile>
  removeAvatar: () => Promise<Profile>
  clear: () => void
}

export const useProfileStore = create<ProfileStore>((set) => ({
  profile: null,
  isLoading: false,

  load: async () => {
    set({ isLoading: true })
    try {
      const profile = await profileService.get()
      set({ profile, isLoading: false })
    } catch (err) {
      set({ isLoading: false })
      showApiErrorToast(err, 'Could not load your profile.')
    }
  },

  save: async (payload) => {
    const profile = await profileService.update(payload)
    set({ profile })
    return profile
  },

  uploadAvatar: async (file) => {
    const profile = await profileService.uploadAvatar(file)
    set({ profile })
    return profile
  },

  removeAvatar: async () => {
    const profile = await profileService.removeAvatar()
    set({ profile })
    return profile
  },

  clear: () => set({ profile: null, isLoading: false }),
}))
