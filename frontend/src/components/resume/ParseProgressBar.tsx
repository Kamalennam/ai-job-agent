import type { ResumeStatus } from '@/types/resume'
import { getParseProgress, getParseProgressLabel } from '@/utils/parseProgress'

interface ParseProgressBarProps {
  status: ResumeStatus
  createdAt: string
}

export function ParseProgressBar({ status, createdAt }: ParseProgressBarProps) {
  if (status === 'failed') {
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="status-failed inline-block">{getParseProgressLabel(status)}</span>
        </div>
        <div className="progress-track">
          <div className="progress-fill-error" />
        </div>
      </div>
    )
  }

  if (status === 'parsed') {
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="status-parsed inline-block">{getParseProgressLabel(status)}</span>
          <span className="status-parsed inline-block font-medium">100%</span>
        </div>
        <div className="progress-track">
          <div className="progress-fill-success" />
        </div>
      </div>
    )
  }

  const progress = Math.round(getParseProgress(status, createdAt))

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted">{getParseProgressLabel(status)}</span>
        <span className="font-medium" style={{ color: 'var(--color-brand)' }}>
          {progress}%
        </span>
      </div>
      <div className="progress-track">
        <div className="progress-fill-brand" style={{ width: `${progress}%` }} />
      </div>
    </div>
  )
}
