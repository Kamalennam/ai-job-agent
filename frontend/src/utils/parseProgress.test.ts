import { describe, expect, it } from 'vitest'
import { getParseProgress, isParseInProgress } from './parseProgress'

describe('parseProgress', () => {
  const createdAt = '2026-01-01T00:00:00.000Z'

  it('returns 100 for parsed resumes', () => {
    expect(getParseProgress('parsed', createdAt)).toBe(100)
  })

  it('returns 0 for failed resumes', () => {
    expect(getParseProgress('failed', createdAt)).toBe(0)
  })

  it('increases progress while parsing', () => {
    const start = new Date(createdAt).getTime()
    const early = getParseProgress('parsing', createdAt, start + 5_000)
    const later = getParseProgress('parsing', createdAt, start + 45_000)
    expect(later).toBeGreaterThan(early)
    expect(later).toBeLessThanOrEqual(95)
  })

  it('detects in-progress statuses', () => {
    expect(isParseInProgress('pending')).toBe(true)
    expect(isParseInProgress('parsing')).toBe(true)
    expect(isParseInProgress('parsed')).toBe(false)
  })
})
