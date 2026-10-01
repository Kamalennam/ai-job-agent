import { NavLink } from 'react-router-dom'
import { navItems } from './navItems'

export function MobileNav() {
  return (
    <nav
      aria-label="Main navigation"
      className="app-mobile-nav fixed inset-x-0 bottom-0 z-40 border-t pb-[env(safe-area-inset-bottom)] md:hidden"
    >
      <div className="flex items-stretch justify-around">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              [
                'flex flex-1 flex-col items-center justify-center gap-0.5 rounded-none px-2 py-3 text-xs font-medium transition-colors',
                isActive ? 'nav-link-active' : 'nav-link-idle',
              ].join(' ')
            }
          >
            {item.label}
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
