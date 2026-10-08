import { describe, expect, it } from 'vitest'
import { displayParseProgress, getParseStageLabel, isParseInProgress } from './parseProgress'

describe('parseProgress', () => {
  it('uses the server progress while content is parsing', () => {
    expect(displayParseProgress('parsing', 42)).toBe(42)
    expect(displayParseProgress('parsing', 90)).toBe(90)
  })

  it('shows 100 only when parsing is complete', () => {
    expect(displayParseProgress('parsed', 28)).toBe(100)
  })

  it('labels each real parse stage', () => {
    expect(getParseStageLabel('queued', 'pending')).toBe('Queued for parsing…')
    expect(getParseStageLabel('reading', 'parsing')).toBe('Reading the PDF…')
    expect(getParseStageLabel('extracting', 'parsing')).toBe('Extracting text…')
    expect(getParseStageLabel('analyzing', 'parsing')).toBe('Parsing resume content…')
    expect(getParseStageLabel('saving', 'parsing')).toBe('Saving extracted profile…')
    expect(getParseStageLabel('complete', 'parsed')).toBe('Parsing complete')
  })

  it('detects in-progress statuses', () => {
    expect(isParseInProgress('pending')).toBe(true)
    expect(isParseInProgress('parsing')).toBe(true)
    expect(isParseInProgress('parsed')).toBe(false)
  })
})
