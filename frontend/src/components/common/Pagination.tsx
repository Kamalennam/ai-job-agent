type PaginationProps = {
  page: number
  pageSize: number
  total: number
  disabled?: boolean
  onPageChange: (page: number) => void
}

function pageWindow(page: number, pageCount: number): number[] {
  const start = Math.max(1, Math.min(page - 2, pageCount - 4))
  const end = Math.min(pageCount, start + 4)
  const pages: number[] = []
  for (let number = Math.max(1, end - 4); number <= end; number += 1) {
    pages.push(number)
  }
  return pages
}

export function Pagination({ page, pageSize, total, disabled = false, onPageChange }: PaginationProps) {
  if (total <= 0) return null

  const pageCount = Math.max(1, Math.ceil(total / pageSize))
  const current = Math.min(page, pageCount)
  const from = (current - 1) * pageSize + 1
  const to = Math.min(current * pageSize, total)
  const pages = pageWindow(current, pageCount)

  return (
    <nav className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between" aria-label="Job pages">
      <p className="text-muted text-sm">
        {from}–{to} of {total}
        <span className="text-subtle"> · highest match first</span>
      </p>
      {pageCount > 1 && (
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            className="btn-secondary"
            disabled={disabled || current <= 1}
            onClick={() => onPageChange(current - 1)}
          >
            Previous
          </button>
          {pages.map((number) => (
            <button
              key={number}
              type="button"
              className={number === current ? 'btn-primary px-3' : 'btn-secondary px-3'}
              disabled={disabled || number === current}
              aria-current={number === current ? 'page' : undefined}
              onClick={() => onPageChange(number)}
            >
              {number}
            </button>
          ))}
          <button
            type="button"
            className="btn-secondary"
            disabled={disabled || current >= pageCount}
            onClick={() => onPageChange(current + 1)}
          >
            Next
          </button>
        </div>
      )}
    </nav>
  )
}
