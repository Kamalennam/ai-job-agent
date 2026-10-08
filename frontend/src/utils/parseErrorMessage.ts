const FALLBACK = 'Parsing failed. Upload the resume again or choose another file.'

export function parseFailureMessage(error: string | null | undefined): string {
  if (!error || /https?:\/\/|ollama|traceback|client error/i.test(error)) {
    return FALLBACK
  }
  return error
}
