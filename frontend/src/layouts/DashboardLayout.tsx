import { Outlet } from 'react-router-dom'
import { MobileNav } from '@/components/layout/MobileNav'
import { Navbar } from '@/components/layout/Navbar'
import { Sidebar } from '@/components/layout/Sidebar'

export function DashboardLayout() {
  return (
    <div className="app-shell flex min-h-screen">
      <Sidebar />
      <div className="flex min-h-screen min-w-0 flex-1 flex-col">
        <Navbar />
        <main className="flex-1 overflow-x-hidden p-4 pb-24 sm:p-6 md:pb-6">
          <Outlet />
        </main>
        <MobileNav />
      </div>
    </div>
  )
}
