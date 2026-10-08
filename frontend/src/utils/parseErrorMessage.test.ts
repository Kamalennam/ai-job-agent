import { describe, expect, it } from 'vitest'
import { parseFailureMessage } from './parseErrorMessage'

describe('parseFailureMessage', () => {
  it('hides Ollama HTTP errors', () => {
    const raw =
      "Ollama request failed: Client error '404 Not Found' for url 'http://localhost:11434/api/generate'"
    expect(parseFailureMessage(raw)).toBe(
      'Parsing failed. Upload the resume again or choose another file.',
    )
  })

  it('shows a message that is already safe', () => {
    const message = 'No text could be read from this PDF. Try another file.'
    expect(parseFailureMessage(message)).toBe(message)
  })
})
