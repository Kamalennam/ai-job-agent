import { useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'

export function AuthBootstrap({ children }: { children: React.ReactNode }) {
  const initialize = useAuthStore((state) => state.initialize)
  const isInitializing = useAuthStore((state) => state.isInitializing)

  useEffect(() => {
    void initialize()
  }, [initialize])

  if (isInitializing) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-surface-muted">
        <p className="text-sm text-slate-500">Loading...</p>
      </div>
    )
  }

  return <>{children}</>
}
