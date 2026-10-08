import { useCallback, useEffect, useRef, useState } from 'react'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { ParseProgressBar } from '@/components/resume/ParseProgressBar'
import { ResumeDeleteButton } from '@/components/resume/ResumeDeleteButton'
import { ResumeUploader } from '@/components/resume/ResumeUploader'
import { ResumeViewButton } from '@/components/resume/ResumeViewButton'
import { resumeService } from '@/services/resumeService'
import { showApiErrorToast } from '@/utils/apiError'
import { parseFailureMessage } from '@/utils/parseErrorMessage'
import { downloadResumeFile } from '@/utils/resumeDownload'
import { showErrorToast, showSuccessToast } from '@/store/toastStore'
import type { Resume, ResumeDetail } from '@/types/resume'

const POLL_INTERVAL_MS = 1000

function StatusBadge({ status }: { status: Resume['status'] }) {
  const styles: Record<Resume['status'], string> = {
    pending: 'status-pending',
    parsing: 'status-parsing',
    parsed: 'status-parsed',
    failed: 'status-failed',
  }

  return <span className={`shrink-0 ${styles[status]}`}>{status}</span>
}

function mergeResumeIntoList(current: Resume[], uploaded: Resume): Resume[] {
  return [uploaded, ...current.filter((item) => item.id !== uploaded.id)]
}

export function ResumeManagerPage() {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [detail, setDetail] = useState<ResumeDetail | null>(null)
  const [pendingDelete, setPendingDelete] = useState<Pick<Resume, 'id' | 'filename'> | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const parseFailureNotified = useRef(false)

  const refreshList = useCallback(async () => {
    const response = await resumeService.list()
    setResumes(response.items)
    return response.items
  }, [])

  const loadDetail = useCallback(async (resumeId: string) => {
    const response = await resumeService.get(resumeId)
    setDetail(response)
    setResumes((prev) => prev.map((resume) => (resume.id === resumeId ? { ...resume, ...response } : resume)))
    return response
  }, [])

  useEffect(() => {
    void refreshList().catch((err) => showApiErrorToast(err, 'Could not load resumes.'))
  }, [refreshList])

  useEffect(() => {
    if (!selectedId) {
      setDetail(null)
      return
    }

    let cancelled = false
    let intervalId: number | undefined

    const poll = async (): Promise<Resume['status'] | 'error'> => {
      try {
        const response = await loadDetail(selectedId)
        if (cancelled) return 'error'
        return response.status
      } catch (err) {
        if (!cancelled) showApiErrorToast(err, 'Could not load resume details.')
        return 'error'
      }
    }

    const stopPolling = () => {
      if (intervalId !== undefined) {
        window.clearInterval(intervalId)
        intervalId = undefined
      }
    }

    void (async () => {
      const status = await poll()
      if (cancelled) return

      if (status === 'parsed' || status === 'failed' || status === 'error') {
        return
      }

      intervalId = window.setInterval(() => {
        void (async () => {
          const nextStatus = await poll()
          if (nextStatus === 'parsed' || nextStatus === 'failed' || nextStatus === 'error') {
            stopPolling()
          }
        })()
      }, POLL_INTERVAL_MS)
    })()

    return () => {
      cancelled = true
      stopPolling()
    }
  }, [selectedId, loadDetail])

  useEffect(() => {
    if (detail?.status === 'failed' && !parseFailureNotified.current) {
      parseFailureNotified.current = true
      showErrorToast('Resume parsing failed. Try uploading again.')
    }
    if (detail?.status !== 'failed') {
      parseFailureNotified.current = false
    }
  }, [detail?.status])

  const handleUploaded = (resume: Resume) => {
    setResumes((prev) => mergeResumeIntoList(prev, resume))
    setSelectedId(resume.id)
    setDetail({
      ...resume,
      parse_progress: resume.parse_progress ?? 0,
      parse_stage: resume.parse_stage ?? 'queued',
      parse_error: null,
      parsed_resume: null,
    })
    void refreshList().catch((err) => showApiErrorToast(err, 'Could not refresh resume list.'))
  }

  const requestDelete = (resume: Pick<Resume, 'id' | 'filename'>) => {
    setPendingDelete({ id: resume.id, filename: resume.filename })
  }

  const cancelDelete = () => {
    if (deletingId) return
    setPendingDelete(null)
  }

  const confirmDelete = async () => {
    if (!pendingDelete) return
    const resume = pendingDelete

    setDeletingId(resume.id)
    try {
      await resumeService.delete(resume.id)
      setResumes((prev) => prev.filter((item) => item.id !== resume.id))
      if (selectedId === resume.id) {
        setSelectedId(null)
        setDetail(null)
      }
      setPendingDelete(null)
      showSuccessToast('Resume deleted.')
    } catch (err) {
      showApiErrorToast(err, 'Could not delete resume.')
    } finally {
      setDeletingId(null)
    }
  }

  const handleDownload = (resume: Pick<Resume, 'file_url' | 'filename'>) => {
    if (!downloadResumeFile(resume)) {
      showErrorToast('Download URL not available for this resume.')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Resumes</h1>
        <p className="page-subtitle">Upload a PDF and verify extracted text.</p>
      </div>

      <ConfirmDialog
        open={pendingDelete !== null}
        title="Delete this resume?"
        description={
          pendingDelete
            ? `"${pendingDelete.filename}" will be removed permanently, including the PDF, its parsed profile, and any job matches for this file.`
            : ''
        }
        confirmLabel="Delete resume"
        pending={deletingId !== null}
        onConfirm={() => void confirmDelete()}
        onCancel={cancelDelete}
      />

      <ResumeUploader onUploaded={handleUploaded} />

      <div className="grid gap-6 lg:grid-cols-[16rem_1fr]">
        <div className="panel p-4">
          <h2 className="text-sm font-semibold">Your uploads</h2>
          {resumes.length === 0 ? (
            <p className="text-muted mt-3 text-sm">No resumes yet.</p>
          ) : (
            <ul className="mt-3 space-y-2">
              {resumes.map((resume) => (
                <li key={resume.id}>
                  <div
                    className={[
                      'flex items-center gap-1 rounded-lg px-3 py-2 text-sm transition-colors',
                      selectedId === resume.id ? 'nav-link-active' : 'nav-link-idle hover:bg-[var(--color-hover)]',
                    ].join(' ')}
                  >
                    <button
                      type="button"
                      onClick={() => setSelectedId(resume.id)}
                      className="min-w-0 flex-1 truncate text-left font-medium"
                    >
                      {resume.filename}
                    </button>
                    <ResumeViewButton onClick={() => handleDownload(resume)} />
                    <ResumeDeleteButton
                      disabled={deletingId === resume.id}
                      onClick={() => requestDelete(resume)}
                    />
                    <StatusBadge status={resume.status} />
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="panel p-6">
          {!detail ? (
            <p className="text-muted text-sm">Select a resume to view extracted text.</p>
          ) : (
            <div className="space-y-4">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <h2 className="text-lg font-semibold">{detail.filename}</h2>
                  <p className="text-muted text-sm">
                    Parser: {detail.parsed_resume?.parser_version ?? '—'}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <ResumeViewButton onClick={() => handleDownload(detail)} />
                  <ResumeDeleteButton
                    disabled={deletingId === detail.id}
                    onClick={() => requestDelete(detail)}
                  />
                  <StatusBadge status={detail.status} />
                </div>
              </div>

              {(detail.status === 'pending' ||
                detail.status === 'parsing' ||
                detail.status === 'parsed' ||
                detail.status === 'failed') && (
                <ParseProgressBar
                  status={detail.status}
                  progress={detail.parse_progress ?? 0}
                  stage={detail.parse_stage ?? 'queued'}
                />
              )}

              {detail.status === 'failed' && (
                <p className="text-muted text-sm">{parseFailureMessage(detail.parse_error)}</p>
              )}

              {detail.parsed_resume && detail.parsed_resume.skills.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold">Skills</h3>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {detail.parsed_resume.skills.map((skill) => (
                      <span key={skill} className="chip-brand">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {detail.parsed_resume && detail.parsed_resume.experience.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold">Experience</h3>
                  <ul className="mt-2 space-y-3">
                    {detail.parsed_resume.experience.map((item) => (
                      <li key={`${item.company}-${item.title}`} className="surface-muted-block">
                        <p className="text-sm font-medium">
                          {item.title} · {item.company}
                        </p>
                        <p className="text-subtle text-xs">
                          {[item.start_date, item.end_date ?? 'Present'].filter(Boolean).join(' – ')}
                        </p>
                        {item.description && (
                          <p className="text-muted mt-1 text-sm">{item.description}</p>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {detail.parsed_resume && detail.parsed_resume.projects.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold">Projects</h3>
                  <ul className="mt-2 space-y-3">
                    {detail.parsed_resume.projects.map((project) => (
                      <li key={project.name} className="surface-muted-block">
                        <p className="text-sm font-medium">{project.name}</p>
                        {project.description && (
                          <p className="text-muted mt-1 text-sm">{project.description}</p>
                        )}
                        {project.technologies.length > 0 && (
                          <p className="text-subtle mt-2 text-xs">
                            {project.technologies.join(', ')}
                          </p>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {detail.parsed_resume?.summary && (
                <div>
                  <h3 className="text-sm font-semibold">Summary</h3>
                  <p className="text-muted mt-2 text-sm">{detail.parsed_resume.summary}</p>
                </div>
              )}

              {detail.parsed_resume?.raw_text && (
                <div>
                  <h3 className="text-sm font-semibold">Extracted text</h3>
                  <pre className="surface-muted-block text-muted mt-2 max-h-[32rem] overflow-auto whitespace-pre-wrap text-sm">
                    {detail.parsed_resume.raw_text}
                  </pre>
                </div>
              )}

              {detail.parsed_resume && (
                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="surface-muted-block">
                    <p className="text-subtle text-xs uppercase">Name</p>
                    <p className="text-sm">{detail.parsed_resume.name ?? '—'}</p>
                  </div>
                  <div className="surface-muted-block">
                    <p className="text-subtle text-xs uppercase">Email</p>
                    <p className="text-sm">{detail.parsed_resume.email ?? '—'}</p>
                  </div>
                  <div className="surface-muted-block">
                    <p className="text-subtle text-xs uppercase">Phone</p>
                    <p className="text-sm">{detail.parsed_resume.phone ?? '—'}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
