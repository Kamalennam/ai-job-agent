import type { MouseEvent } from 'react'

function EyeIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  )
}

export function ResumeViewButton({
  onClick,
  title = 'View or download resume',
}: {
  onClick: (event: MouseEvent<HTMLButtonElement>) => void
  title?: string
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={title}
      aria-label={title}
      className="shrink-0 rounded-md p-1 transition-colors hover:bg-[var(--color-hover)]"
      style={{ color: 'var(--color-text-muted)' }}
    >
      <EyeIcon className="h-4 w-4" />
    </button>
  )
}
