import { Outlet } from 'react-router-dom'

export function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-muted px-4">
      <div className="w-full max-w-md rounded-xl border border-surface-border bg-white p-8 shadow-sm">
        <Outlet />
      </div>
    </div>
  )
}
