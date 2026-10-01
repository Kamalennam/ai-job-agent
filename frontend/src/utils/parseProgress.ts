import type { ResumeStatus } from '@/types/resume'

const PENDING_BASE = 12
const PENDING_MAX = 22
const PARSING_BASE = 25
const PARSING_MAX = 95
const ESTIMATED_PARSE_MS = 90_000

export function getParseProgress(status: ResumeStatus, createdAt: string, now = Date.now()): number {
  const elapsed = Math.max(0, now - new Date(createdAt).getTime())

  switch (status) {
    case 'pending':
      return Math.min(PENDING_MAX, PENDING_BASE + elapsed / 2000)
    case 'parsing':
      return Math.min(PARSING_MAX, PARSING_BASE + (elapsed / ESTIMATED_PARSE_MS) * (PARSING_MAX - PARSING_BASE))
    case 'parsed':
      return 100
    case 'failed':
      return 0
  }
}

export function getParseProgressLabel(status: ResumeStatus): string {
  switch (status) {
    case 'pending':
      return 'Queued for parsing…'
    case 'parsing':
      return 'Extracting text and running AI analysis…'
    case 'parsed':
      return 'Parsing complete'
    case 'failed':
      return 'Parsing failed'
  }
}

export function isParseInProgress(status: ResumeStatus): boolean {
  return status === 'pending' || status === 'parsing'
}
