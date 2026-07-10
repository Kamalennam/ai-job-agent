import { useNavigate } from 'react-router-dom'
import { useTheme } from '@/app/ThemeProvider'
import { useAuthStore } from '@/store/authStore'

export function Navbar() {
  const navigate = useNavigate()
  const logout = useAuthStore((state) => state.logout)
  const { mode, toggleMode } = useTheme()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <header className="flex h-16 items-center justify-between border-b border-surface-border bg-white px-6">
      <div>
        <p className="text-sm text-slate-500">Overview</p>
        <h1 className="text-lg font-semibold text-slate-900">Dashboard</h1>
      </div>
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={toggleMode}
          className="rounded-lg border border-surface-border px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-50"
        >
          {mode === 'light' ? 'Dark' : 'Light'}
        </button>
        <button
          type="button"
          onClick={handleLogout}
          className="rounded-lg bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700"
        >
          Logout
        </button>
      </div>
    </header>
  )
}
