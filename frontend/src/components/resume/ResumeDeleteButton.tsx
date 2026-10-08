import type { MouseEvent } from 'react'

function TrashIcon({ className }: { className?: string }) {
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
      <path d="M3 6h18" />
      <path d="M8 6V4h8v2" />
      <path d="M19 6l-1 14H6L5 6" />
      <path d="M10 11v6" />
      <path d="M14 11v6" />
    </svg>
  )
}

export function ResumeDeleteButton({
  onClick,
  disabled = false,
  title = 'Delete resume',
}: {
  onClick: (event: MouseEvent<HTMLButtonElement>) => void
  disabled?: boolean
  title?: string
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={title}
      aria-label={title}
      className="shrink-0 rounded-md p-1 text-[color:var(--color-text-muted)] transition-colors hover:bg-[var(--color-hover)] hover:text-red-600 disabled:opacity-50"
    >
      <TrashIcon className="h-4 w-4" />
    </button>
  )
}
