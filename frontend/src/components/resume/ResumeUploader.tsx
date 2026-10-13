import { DragEvent, FormEvent, useRef, useState } from 'react'
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
  const [isDragging, setIsDragging] = useState(false)
  const [fileName, setFileName] = useState<string | null>(null)

  const assignFile = (file: File | null) => {
    if (!file || !inputRef.current) {
      setFileName(null)
      return
    }
    const transfer = new DataTransfer()
    transfer.items.add(file)
    inputRef.current.files = transfer.files
    setFileName(file.name)
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const file = inputRef.current?.files?.[0]
    if (!file) {
      showErrorToast('Please choose a PDF file.')
      return
    }

    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      showErrorToast('Only PDF files are supported.')
      return
    }

    setIsUploading(true)

    try {
      const resume = await resumeService.upload(file, isPrimary)
      showSuccessToast('Resume saved. Parsing has started.')
      onUploaded(resume)
      assignFile(null)
      if (inputRef.current) {
        inputRef.current.value = ''
      }
      setFileName(null)
    } catch (err) {
      showApiErrorToast(err, 'Upload failed. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  const handleDrop = (event: DragEvent<HTMLLabelElement>) => {
    event.preventDefault()
    setIsDragging(false)
    if (isUploading) return
    assignFile(event.dataTransfer.files?.[0] ?? null)
  }

  return (
    <form onSubmit={handleSubmit} className="panel p-6">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">Upload resume</h2>
          <p className="page-subtitle">PDF only. The file is saved first, then parsing starts.</p>
        </div>
      </div>

      <label
        className={['dropzone mt-4', isDragging ? 'dropzone-active' : '', isUploading ? 'dropzone-busy' : ''].join(' ')}
        onDragOver={(event) => {
          event.preventDefault()
          if (!isUploading) setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          disabled={isUploading}
          className="sr-only"
          onChange={(event) => setFileName(event.target.files?.[0]?.name ?? null)}
        />
        <span className="text-sm font-medium">
          {isUploading ? 'Saving to your account...' : fileName ?? 'Drop a PDF here, or browse'}
        </span>
        <span className="text-subtle mt-1 block text-xs">
          {isUploading ? 'It will appear in the list as soon as the upload finishes.' : 'Maximum 10 MB'}
        </span>
      </label>

      <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <label className="text-muted flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={isPrimary}
            onChange={(event) => setIsPrimary(event.target.checked)}
            className="input-checkbox"
            disabled={isUploading}
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
