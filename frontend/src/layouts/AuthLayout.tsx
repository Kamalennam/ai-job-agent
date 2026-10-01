import { Outlet } from 'react-router-dom'
import { ThemeToggle } from '@/components/layout/ThemeToggle'

export function AuthLayout() {
  return (
    <div className="app-shell relative flex min-h-screen items-center justify-center px-4 py-8">
      <div className="absolute right-4 top-4 sm:right-6 sm:top-6">
        <ThemeToggle showLabel />
      </div>
      <div className="panel w-full max-w-md p-6 sm:p-8">
        <Outlet />
      </div>
    </div>
  )
}
