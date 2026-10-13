import { Outlet } from 'react-router-dom'
import { ThemeToggle } from '@/components/layout/ThemeToggle'

const points = [
  'Upload a resume PDF',
  'We read it and match collected jobs',
  'Review the strongest fits in one place',
]

export function AuthLayout() {
  return (
    <div className="app-shell grid min-h-screen lg:grid-cols-[minmax(0,1.05fr)_minmax(22rem,0.95fr)]">
      <section className="auth-hero hidden lg:flex">
        <div className="max-w-md">
          <div className="flex items-center gap-3">
            <span className="brand-mark" aria-hidden="true">
              A
            </span>
            <p className="text-sm font-semibold tracking-wide text-white">AI Job Agent</p>
          </div>
          <p className="mt-10 text-4xl font-semibold leading-tight text-white">
            A quieter way to run a job search.
          </p>
          <p className="mt-4 text-sm leading-6 text-slate-300">
            Keep the resume, the matches, and the next step in one workspace.
          </p>
          <ul className="mt-8 space-y-3">
            {points.map((point) => (
              <li key={point} className="flex items-center gap-3 text-sm text-slate-200">
                <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-indigo-300" aria-hidden="true" />
                {point}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <div className="relative flex items-center justify-center px-4 py-8">
        <div className="absolute right-4 top-4 sm:right-6 sm:top-6">
          <ThemeToggle />
        </div>
        <div className="w-full max-w-md">
          <p className="mb-6 text-center text-sm font-semibold lg:hidden">AI Job Agent</p>
          <div className="panel p-6 sm:p-8">
            <Outlet />
          </div>
        </div>
      </div>
    </div>
  )
}
