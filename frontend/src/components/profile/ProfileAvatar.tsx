import { useEffect, useState } from 'react'

function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean)
  if (parts.length === 0) return 'P'
  if (parts.length === 1) return parts[0].slice(0, 1).toUpperCase()
  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
}

const sizeClass = {
  sm: '',
  lg: 'profile-avatar-lg',
  preview: 'profile-avatar-preview',
} as const

export function ProfileAvatar({
  name,
  url,
  size = 'sm',
}: {
  name: string
  url: string | null
  size?: keyof typeof sizeClass
}) {
  const [failed, setFailed] = useState(false)
  const showImage = Boolean(url) && !failed

  useEffect(() => {
    setFailed(false)
  }, [url])

  return (
    <span className={['profile-avatar', sizeClass[size]].filter(Boolean).join(' ')}>
      {showImage ? (
        <img src={url ?? undefined} alt="" onError={() => setFailed(true)} />
      ) : (
        initials(name)
      )}
    </span>
  )
}
