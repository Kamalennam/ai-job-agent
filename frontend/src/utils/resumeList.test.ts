import { describe, expect, it } from 'vitest'
import { applyResumeList } from './resumeList'
import type { Resume } from '@/types/resume'

function resume(overrides: Partial<Resume> & Pick<Resume, 'id'>): Resume {
  return {
    filename: 'resume.pdf',
    file_url: null,
    status: 'pending',
    is_primary: false,
    parse_progress: 0,
    parse_stage: 'queued',
    created_at: '2026-10-13T00:00:00Z',
    ...overrides,
  }
}

describe('applyResumeList', () => {
  it('keeps a resume the server list has not returned yet', () => {
    const uploaded = resume({ id: 'new', filename: 'new.pdf', parse_progress: 0 })
    const existing = resume({ id: 'old', filename: 'old.pdf', status: 'parsed', parse_progress: 100 })

    const next = applyResumeList([existing], [uploaded, existing])

    expect(next.map((item) => item.id)).toEqual(['new', 'old'])
  })

  it('does not replace newer parse progress with an older snapshot', () => {
    const local = resume({ id: 'resume', status: 'parsing', parse_progress: 40, parse_stage: 'analyzing' })
    const server = resume({ id: 'resume', status: 'pending', parse_progress: 8, parse_stage: 'reading' })

    const next = applyResumeList([server], [local])

    expect(next[0]?.status).toBe('parsing')
    expect(next[0]?.parse_progress).toBe(40)
  })

  it('uses the server row when parsing has moved further', () => {
    const local = resume({ id: 'resume', status: 'parsing', parse_progress: 20, parse_stage: 'extracting' })
    const server = resume({ id: 'resume', status: 'parsed', parse_progress: 100, parse_stage: 'complete' })

    const next = applyResumeList([server], [local])

    expect(next[0]?.status).toBe('parsed')
    expect(next[0]?.parse_progress).toBe(100)
  })
})
