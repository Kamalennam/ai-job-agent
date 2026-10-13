import { useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import { MobileNav } from '@/components/layout/MobileNav'
import { Navbar } from '@/components/layout/Navbar'
import { Sidebar } from '@/components/layout/Sidebar'
import { useAuthStore } from '@/store/authStore'
import { useProfileStore } from '@/store/profileStore'

export function DashboardLayout() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const loadProfile = useProfileStore((state) => state.load)
  const clearProfile = useProfileStore((state) => state.clear)

  useEffect(() => {
    if (!isAuthenticated) {
      clearProfile()
      return
    }
    void loadProfile()
  }, [clearProfile, isAuthenticated, loadProfile])

  return (
    <div className="app-shell flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex h-full min-w-0 flex-1 flex-col overflow-hidden">
        <Navbar />
        <main className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden p-4 pb-24 sm:p-6 md:pb-6">
          <Outlet />
        </main>
        <MobileNav />
      </div>
    </div>
  )
}
