import { FormEvent, useRef, useState } from 'react'
import { resumeService } from '@/services/resumeService'
import { showErrorToast, showSuccessToast } from '@/store/toastStore'
import { showApiErrorToast } from '@/utils/apiError'

interface ResumeUploaderProps {
  onUploaded: (resumeId: string) => void
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
      onUploaded(resume.id)
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
    <form
      onSubmit={handleSubmit}
      className="rounded-xl border border-surface-border bg-white p-6 shadow-sm"
    >
      <h2 className="text-lg font-semibold text-slate-900">Upload resume</h2>
      <p className="mt-1 text-sm text-slate-500">PDF only. Text will be extracted automatically.</p>

      <div className="mt-4 space-y-4">
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          className="block w-full text-sm text-slate-600 file:mr-4 file:rounded-lg file:border-0 file:bg-brand-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-brand-700 hover:file:bg-brand-100"
        />
        <label className="flex items-center gap-2 text-sm text-slate-600">
          <input
            type="checkbox"
            checked={isPrimary}
            onChange={(event) => setIsPrimary(event.target.checked)}
            className="rounded border-surface-border text-brand-600 focus:ring-brand-500"
          />
          Set as primary resume
        </label>
        <button
          type="submit"
          disabled={isUploading}
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
        >
          {isUploading ? 'Uploading...' : 'Upload PDF'}
        </button>
      </div>
    </form>
  )
}
