import { FormEvent, useRef, useState } from 'react'
import { resumeService } from '@/services/resumeService'
import { showErrorToast, showSuccessToast } from '@/store/toastStore'
import { showApiErrorToast } from '@/utils/apiError'
import type { Resume } from '@/types/resume'

interface ResumeUploaderProps {
  onUploaded: (resume: Resume) => void
}

export function ResumeUploader({ onUploaded }: ResumeUploaderProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [isPrimary, setIsPrimary] = useState(true)
  const [isUploading, setIsUploading] = useState(false)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const file = inputRef.current?.files?.[0]
    if (!file) {
      showErrorToast('Please choose a PDF file.')
      return
    }

    if (file.type !== 'application/pdf') {
      showErrorToast('Only PDF files are supported.')
      return
    }

    setIsUploading(true)

    try {
      const resume = await resumeService.upload(file, isPrimary)
      showSuccessToast('Resume uploaded. Parsing will start shortly.')
      onUploaded(resume)
      if (inputRef.current) {
        inputRef.current.value = ''
      }
    } catch (err) {
      showApiErrorToast(err, 'Upload failed. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="panel p-6">
      <h2 className="text-lg font-semibold">Upload resume</h2>
      <p className="page-subtitle">PDF only. Text will be extracted automatically.</p>

      <div className="mt-4 space-y-4">
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          className="text-muted block w-full text-sm file:mr-4 file:rounded-lg file:border-0 file:bg-[color:var(--color-brand-soft)] file:px-4 file:py-2 file:text-sm file:font-medium file:text-[color:var(--color-brand-soft-text)] hover:file:opacity-90"
        />
        <label className="text-muted flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={isPrimary}
            onChange={(event) => setIsPrimary(event.target.checked)}
            className="input-checkbox"
          />
          Set as primary resume
        </label>
        <button type="submit" disabled={isUploading} className="btn-primary disabled:opacity-60">
          {isUploading ? 'Uploading...' : 'Upload PDF'}
        </button>
      </div>
    </form>
  )
}
