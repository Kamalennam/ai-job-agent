import { NavLink } from 'react-router-dom'
import { ProfileAvatar } from '@/components/profile/ProfileAvatar'
import { useProfileStore } from '@/store/profileStore'

export function ProfileAccount({ variant }: { variant: 'sidebar' | 'header' }) {
  const profile = useProfileStore((state) => state.profile)
  const name = profile?.full_name || 'Profile'
  const className = variant === 'sidebar' ? 'profile-chip-sidebar' : 'profile-chip'

  return (
    <NavLink
      to="/profile"
      className={({ isActive }) =>
        [className, isActive && variant === 'sidebar' ? 'profile-chip-sidebar-active' : ''].join(' ')
      }
      title={name}
    >
      <ProfileAvatar name={name} url={profile?.avatar_url ?? null} />
      <span className={variant === 'header' ? 'hidden min-w-0 sm:block' : 'min-w-0'}>
        <span className="block truncate text-sm font-medium">{name}</span>
        {variant === 'sidebar' && (
          <span className="sidebar-muted block truncate text-xs">{profile?.email ?? 'Account'}</span>
        )}
      </span>
    </NavLink>
  )
}
