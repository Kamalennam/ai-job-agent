import { useLocation, useNavigate } from 'react-router-dom'
import { ProfileAccount } from '@/components/layout/ProfileAccount'
import { ThemeToggle } from '@/components/layout/ThemeToggle'
import { navItems } from '@/components/layout/navItems'
import { useAuthStore } from '@/store/authStore'

function pageTitleFromPath(pathname: string): string {
  const match = navItems.find((item) => pathname.startsWith(item.to))
  if (match) return match.label
  if (pathname.startsWith('/jobs/')) return 'Job detail'
  if (pathname.startsWith('/profile')) return 'Profile'
  return 'Dashboard'
}

export function Navbar() {
  const navigate = useNavigate()
  const location = useLocation()
  const logout = useAuthStore((state) => state.logout)
  const title = pageTitleFromPath(location.pathname)

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <header className="app-header sticky top-0 z-30 flex h-14 shrink-0 items-center justify-between gap-3 border-b px-4 sm:h-16 sm:px-6">
      <div className="min-w-0">
        <p className="truncate text-sm font-semibold md:hidden">AI Job Agent</p>
        <p className="text-subtle hidden text-sm md:block">{title}</p>
      </div>
      <div className="flex shrink-0 items-center gap-2 sm:gap-3">
        <ProfileAccount variant="header" />
        <ThemeToggle />
        <button type="button" onClick={handleLogout} className="btn-secondary px-3 py-1.5">
          Log out
        </button>
      </div>
    </header>
  )
}
