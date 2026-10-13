import { useRef, useState } from 'react'
import { ProfileAvatar } from '@/components/profile/ProfileAvatar'
import { useProfileStore } from '@/store/profileStore'
import { showErrorToast, showSuccessToast } from '@/store/toastStore'
import { showApiErrorToast } from '@/utils/apiError'

const MAX_BYTES = 2 * 1024 * 1024
const ACCEPTED = ['image/jpeg', 'image/png', 'image/webp']

function isAccepted(file: File): boolean {
  if (ACCEPTED.includes(file.type)) return true
  return /\.(jpe?g|png|webp)$/i.test(file.name)
}

export function ProfilePhotoField({ name }: { name: string }) {
  const inputRef = useRef<HTMLInputElement>(null)
  const avatarUrl = useProfileStore((state) => state.profile?.avatar_url ?? null)
  const uploadAvatar = useProfileStore((state) => state.uploadAvatar)
  const removeAvatar = useProfileStore((state) => state.removeAvatar)
  const [isBusy, setIsBusy] = useState<'upload' | 'remove' | null>(null)

  const onFile = async (file: File | undefined) => {
    if (!file) return
    if (!isAccepted(file)) {
      showErrorToast('Use a JPG, PNG, or WebP image.')
      return
    }
    if (file.size > MAX_BYTES) {
      showErrorToast('Photo must be 2 MB or smaller.')
      return
    }

    setIsBusy('upload')
    try {
      await uploadAvatar(file)
      showSuccessToast('Profile photo updated.')
    } catch (err) {
      showApiErrorToast(err, 'Could not upload your photo.')
    } finally {
      setIsBusy(null)
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  const onRemove = async () => {
    setIsBusy('remove')
    try {
      await removeAvatar()
      showSuccessToast('Profile photo removed.')
    } catch (err) {
      showApiErrorToast(err, 'Could not remove your photo.')
    } finally {
      setIsBusy(null)
    }
  }

  return (
    <div>
      <p className="form-label">Profile photo</p>
      <div className="flex items-center gap-4">
        <ProfileAvatar name={name || 'Profile'} url={avatarUrl} size="lg" />
        <div className="min-w-0">
          <div className="flex flex-wrap gap-2">
            <label
              className={['btn-secondary inline-flex items-center', isBusy ? 'pointer-events-none opacity-60' : ''].join(
                ' ',
              )}
            >
              {isBusy === 'upload' ? 'Uploading...' : avatarUrl ? 'Change photo' : 'Upload photo'}
              <input
                ref={inputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="sr-only"
                disabled={isBusy !== null}
                onChange={(event) => void onFile(event.target.files?.[0])}
              />
            </label>
            {avatarUrl && (
              <button type="button" className="btn-secondary" disabled={isBusy !== null} onClick={() => void onRemove()}>
                {isBusy === 'remove' ? 'Removing...' : 'Remove'}
              </button>
            )}
          </div>
          <p className="text-subtle mt-2 text-xs">JPG, PNG, or WebP. Maximum 2 MB. Stored with your account.</p>
        </div>
      </div>
    </div>
  )
}
