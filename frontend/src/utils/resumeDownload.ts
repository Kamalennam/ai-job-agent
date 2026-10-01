import type { Resume } from '@/types/resume'

export function downloadResumeFile(resume: Pick<Resume, 'file_url' | 'filename'>): boolean {
  if (!resume.file_url) {
    return false
  }

  const link = document.createElement('a')
  link.href = resume.file_url
  link.download = resume.filename
  link.target = '_blank'
  link.rel = 'noopener noreferrer'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  return true
}
