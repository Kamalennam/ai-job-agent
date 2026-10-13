import { NavLink } from 'react-router-dom'
import { NavIcon } from './NavIcon'
import { ProfileAccount } from './ProfileAccount'
import { navItems } from './navItems'

export function Sidebar() {
  return (
    <aside className="app-sidebar hidden h-full w-64 shrink-0 overflow-hidden border-r md:flex md:flex-col">
      <div className="flex h-16 items-center gap-3 border-b px-5" style={{ borderColor: 'inherit' }}>
        <span className="brand-mark" aria-hidden="true">
          A
        </span>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold">AI Job Agent</p>
          <p className="sidebar-muted truncate text-xs">Career workspace</p>
        </div>
      </div>
      <nav className="flex min-h-0 flex-1 flex-col gap-1 overflow-y-auto p-3">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              ['sidebar-link', isActive ? 'sidebar-link-active' : ''].join(' ')
            }
          >
            <NavIcon to={item.to} />
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="shrink-0">
        <ProfileAccount variant="sidebar" />
      </div>
    </aside>
  )
}
