import type { ResumeStatus } from '@/types/resume'

export function getParseStageLabel(stage: string | null | undefined, status: ResumeStatus): string {
  if (status === 'failed' || stage === 'failed') {
    return 'Parsing failed'
  }
  if (status === 'parsed' || stage === 'complete') {
    return 'Parsing complete'
  }
  switch (stage) {
    case 'reading':
      return 'Reading the PDF…'
    case 'extracting':
      return 'Extracting text…'
    case 'analyzing':
      return 'Parsing resume content…'
    case 'saving':
      return 'Saving extracted profile…'
    default:
      return 'Queued for parsing…'
  }
}

export function displayParseProgress(status: ResumeStatus, progress: number | null | undefined): number {
  if (status === 'parsed') {
    return 100
  }
  const value = Number.isFinite(progress) ? Number(progress) : 0
  return Math.min(100, Math.max(0, value))
}

export function isParseInProgress(status: ResumeStatus): boolean {
  return status === 'pending' || status === 'parsing'
}
