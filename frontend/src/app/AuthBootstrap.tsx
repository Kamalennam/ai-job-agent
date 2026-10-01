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
      <div className="app-shell flex min-h-screen items-center justify-center">
        <p className="text-muted text-sm">Loading...</p>
      </div>
    )
  }

  return <>{children}</>
}
