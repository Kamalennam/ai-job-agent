import { FormEvent, useEffect, useRef, useState } from 'react'
import { ProfilePhotoField } from '@/components/profile/ProfilePhotoField'
import { ProfilePreviewCard } from '@/components/profile/ProfilePreviewCard'
import { useProfileStore } from '@/store/profileStore'
import { showErrorToast, showSuccessToast } from '@/store/toastStore'
import { showApiErrorToast } from '@/utils/apiError'

function emptyToNull(value: string): string | null {
  const cleaned = value.trim()
  return cleaned || null
}

export function ProfilePage() {
  const profile = useProfileStore((state) => state.profile)
  const isLoading = useProfileStore((state) => state.isLoading)
  const save = useProfileStore((state) => state.save)

  const [fullName, setFullName] = useState('')
  const [headline, setHeadline] = useState('')
  const [location, setLocation] = useState('')
  const [linkedinUrl, setLinkedinUrl] = useState('')
  const [bio, setBio] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const hydratedId = useRef<string | null>(null)

  useEffect(() => {
    if (!profile || hydratedId.current === profile.id) return
    hydratedId.current = profile.id
    setFullName(profile.full_name)
    setHeadline(profile.headline ?? '')
    setLocation(profile.location ?? '')
    setLinkedinUrl(profile.linkedin_url ?? '')
    setBio(profile.bio ?? '')
  }, [profile])

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!fullName.trim()) {
      showErrorToast('Full name is required.')
      return
    }

    setIsSaving(true)
    try {
      await save({
        full_name: fullName.trim(),
        headline: emptyToNull(headline),
        location: emptyToNull(location),
        linkedin_url: emptyToNull(linkedinUrl),
        bio: emptyToNull(bio),
      })
      showSuccessToast('Profile saved.')
    } catch (err) {
      showApiErrorToast(err, 'Could not save your profile.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Profile</h1>
        <p className="page-subtitle">This name is your account name. It is separate from uploaded resumes.</p>
      </div>

      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_22rem]">
        <form onSubmit={handleSubmit} className="panel space-y-4 p-6">
          <div>
            <label htmlFor="email" className="form-label">
              Email
            </label>
            <input id="email" value={profile?.email ?? ''} readOnly className="input-field" />
            <p className="text-subtle mt-1 text-xs">Sign-in email. It is not taken from a resume.</p>
          </div>

          <div>
            <label htmlFor="fullName" className="form-label">
              Full name
            </label>
            <input
              id="fullName"
              required
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              className="input-field"
              maxLength={120}
            />
          </div>

          <ProfilePhotoField name={fullName} />

          <div>
            <label htmlFor="headline" className="form-label">
              Headline
            </label>
            <input
              id="headline"
              value={headline}
              onChange={(event) => setHeadline(event.target.value)}
              className="input-field"
              maxLength={160}
              placeholder="Optional"
            />
          </div>

          <div>
            <label htmlFor="location" className="form-label">
              Location
            </label>
            <input
              id="location"
              value={location}
              onChange={(event) => setLocation(event.target.value)}
              className="input-field"
              maxLength={120}
              placeholder="Optional"
            />
          </div>

          <div>
            <label htmlFor="linkedinUrl" className="form-label">
              LinkedIn URL
            </label>
            <input
              id="linkedinUrl"
              type="url"
              value={linkedinUrl}
              onChange={(event) => setLinkedinUrl(event.target.value)}
              className="input-field"
              maxLength={500}
              placeholder="https://www.linkedin.com/in/..."
            />
          </div>

          <div>
            <label htmlFor="bio" className="form-label">
              Bio
            </label>
            <textarea
              id="bio"
              value={bio}
              onChange={(event) => setBio(event.target.value)}
              className="input-field min-h-28"
              maxLength={2000}
              placeholder="Optional"
            />
          </div>

          <button type="submit" disabled={isSaving || isLoading} className="btn-primary">
            {isSaving ? 'Saving...' : 'Save profile'}
          </button>
        </form>

        <ProfilePreviewCard
          name={fullName}
          email={profile?.email ?? ''}
          emailVerified={profile?.email_verified ?? false}
          headline={headline}
          location={location}
          linkedinUrl={linkedinUrl}
          bio={bio}
          avatarUrl={profile?.avatar_url ?? null}
        />
      </div>
    </div>
  )
}
