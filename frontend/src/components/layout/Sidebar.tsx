import { NavLink } from 'react-router-dom'

const navItems = [
  { label: 'Dashboard', to: '/dashboard' },
  { label: 'Resumes', to: '/resumes' },
  { label: 'Jobs', to: '/jobs' },
]

export function Sidebar() {
  return (
    <aside className="hidden w-64 shrink-0 border-r border-surface-border bg-white md:flex md:flex-col">
      <div className="flex h-16 items-center border-b border-surface-border px-6">
        <span className="text-lg font-semibold text-brand-700">AI Job Agent</span>
      </div>
      <nav className="flex flex-1 flex-col gap-1 p-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              [
                'rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-brand-50 text-brand-700'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900',
              ].join(' ')
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
