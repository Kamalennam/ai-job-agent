import { NavLink } from 'react-router-dom'
import { navItems } from './navItems'

export function Sidebar() {
  return (
    <aside className="app-sidebar hidden w-64 shrink-0 border-r md:flex md:flex-col">
      <div className="flex h-16 items-center border-b px-6" style={{ borderColor: 'var(--color-border)' }}>
        <span className="text-lg font-semibold" style={{ color: 'var(--color-brand)' }}>
          AI Job Agent
        </span>
      </div>
      <nav className="flex flex-1 flex-col gap-1 p-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              ['nav-link', isActive ? 'nav-link-active' : 'nav-link-idle'].join(' ')
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
