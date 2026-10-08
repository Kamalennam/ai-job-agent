import type { ResumeStatus } from '@/types/resume'
import { displayParseProgress, getParseStageLabel } from '@/utils/parseProgress'

interface ParseProgressBarProps {
  status: ResumeStatus
  progress: number
  stage: string
}

export function ParseProgressBar({ status, progress, stage }: ParseProgressBarProps) {
  const label = getParseStageLabel(stage, status)
  const value = displayParseProgress(status, progress)

  if (status === 'failed') {
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="status-failed inline-block">{label}</span>
          <span className="status-failed inline-block font-medium">{value}%</span>
        </div>
        <div className="progress-track">
          <div className="progress-fill-error" style={{ width: `${Math.max(value, 8)}%` }} />
        </div>
      </div>
    )
  }

  if (status === 'parsed') {
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="status-parsed inline-block">{label}</span>
          <span className="status-parsed inline-block font-medium">100%</span>
        </div>
        <div className="progress-track">
          <div className="progress-fill-success" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted">{label}</span>
        <span className="font-medium" style={{ color: 'var(--color-brand)' }}>
          {value}%
        </span>
      </div>
      <div className="progress-track">
        <div className="progress-fill-brand" style={{ width: `${value}%` }} />
      </div>
    </div>
  )
}
