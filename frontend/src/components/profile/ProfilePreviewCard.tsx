import { ProfileAvatar } from '@/components/profile/ProfileAvatar'

interface ProfilePreviewCardProps {
  name: string
  email: string
  emailVerified: boolean
  headline: string
  location: string
  linkedinUrl: string
  bio: string
  avatarUrl: string | null
}

function detail(value: string): string {
  return value.trim()
}

export function ProfilePreviewCard({
  name,
  email,
  emailVerified,
  headline,
  location,
  linkedinUrl,
  bio,
  avatarUrl,
}: ProfilePreviewCardProps) {
  const displayName = detail(name) || 'Your name'
  const displayHeadline = detail(headline)
  const displayLocation = detail(location)
  const displayLinkedin = detail(linkedinUrl)
  const linkedinHref = /^https?:\/\//i.test(displayLinkedin) ? displayLinkedin : ''
  const displayBio = detail(bio)

  return (
    <aside className="panel profile-preview lg:sticky lg:top-6">
      <div className="profile-preview-banner" />
      <div className="profile-preview-body">
        <ProfileAvatar name={displayName} url={avatarUrl} size="preview" />
        <h2 className="mt-3 text-lg font-semibold tracking-tight">{displayName}</h2>
        <p className="text-muted mt-1 text-sm">{displayHeadline || 'Headline appears here'}</p>
        <p className="text-subtle mt-3 text-xs font-medium uppercase tracking-wide">Account</p>
        <dl className="profile-preview-meta">
          <div>
            <dt>Email</dt>
            <dd>
              {email || '—'}
              {emailVerified && <span className="profile-verified">Verified</span>}
            </dd>
          </div>
          <div>
            <dt>Location</dt>
            <dd>{displayLocation || 'Not added'}</dd>
          </div>
          <div>
            <dt>LinkedIn</dt>
            <dd>
              {linkedinHref ? (
                <a href={linkedinHref} target="_blank" rel="noreferrer" className="profile-preview-link">
                  {linkedinHref.replace(/^https?:\/\//, '')}
                </a>
              ) : (
                displayLinkedin || 'Not added'
              )}
            </dd>
          </div>
        </dl>
        <p className="text-subtle mt-4 text-xs font-medium uppercase tracking-wide">Bio</p>
        <p className="mt-1 text-sm leading-6">{displayBio || 'A short bio will show here after you save it.'}</p>
      </div>
    </aside>
  )
}
