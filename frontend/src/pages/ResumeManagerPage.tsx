import { useCallback, useEffect, useRef, useState } from 'react'
import { ResumeUploader } from '@/components/resume/ResumeUploader'
import { resumeService } from '@/services/resumeService'
import { showApiErrorToast } from '@/utils/apiError'
import { showErrorToast } from '@/store/toastStore'
import type { Resume, ResumeDetail } from '@/types/resume'

const POLL_INTERVAL_MS = 2000

function StatusBadge({ status }: { status: Resume['status'] }) {
  const styles: Record<Resume['status'], string> = {
    pending: 'bg-yellow-50 text-yellow-700',
    parsing: 'bg-blue-50 text-blue-700',
    parsed: 'bg-green-50 text-green-700',
    failed: 'bg-red-50 text-red-700',
  }

  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[status]}`}>
      {status}
    </span>
  )
}

export function ResumeManagerPage() {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [detail, setDetail] = useState<ResumeDetail | null>(null)
  const parseFailureNotified = useRef(false)

  const loadList = useCallback(async () => {
    const response = await resumeService.list()
    setResumes(response.items)
    if (response.items.length > 0 && !selectedId) {
      setSelectedId(response.items[0].id)
    }
  }, [selectedId])

  const loadDetail = useCallback(async (resumeId: string) => {
    const response = await resumeService.get(resumeId)
    setDetail(response)
    return response
  }, [])

  useEffect(() => {
    void loadList().catch((err) => showApiErrorToast(err, 'Could not load resumes.'))
  }, [loadList])

  useEffect(() => {
    if (!selectedId) {
      setDetail(null)
      return
    }

    let cancelled = false
    let intervalId: number | undefined

    const poll = async () => {
      try {
        const response = await loadDetail(selectedId)
        if (cancelled) return
        if (response.status === 'parsed' || response.status === 'failed') {
          if (intervalId) window.clearInterval(intervalId)
        }
      } catch (err) {
        if (!cancelled) showApiErrorToast(err, 'Could not load resume details.')
      }
    }

    void poll()
    intervalId = window.setInterval(() => {
      void poll()
    }, POLL_INTERVAL_MS)

    return () => {
      cancelled = true
      if (intervalId) window.clearInterval(intervalId)
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

  const handleUploaded = async (resumeId: string) => {
    await loadList()
    setSelectedId(resumeId)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Resumes</h1>
        <p className="mt-1 text-sm text-slate-500">Upload a PDF and verify extracted text.</p>
      </div>

      <ResumeUploader onUploaded={handleUploaded} />

      <div className="grid gap-6 lg:grid-cols-[16rem_1fr]">
        <div className="rounded-xl border border-surface-border bg-white p-4 shadow-sm">
          <h2 className="text-sm font-semibold text-slate-900">Your uploads</h2>
          {resumes.length === 0 ? (
            <p className="mt-3 text-sm text-slate-500">No resumes yet.</p>
          ) : (
            <ul className="mt-3 space-y-2">
              {resumes.map((resume) => (
                <li key={resume.id}>
                  <button
                    type="button"
                    onClick={() => setSelectedId(resume.id)}
                    className={[
                      'w-full rounded-lg px-3 py-2 text-left text-sm transition-colors',
                      selectedId === resume.id
                        ? 'bg-brand-50 text-brand-700'
                        : 'text-slate-600 hover:bg-slate-50',
                    ].join(' ')}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="truncate font-medium">{resume.filename}</span>
                      <StatusBadge status={resume.status} />
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="rounded-xl border border-surface-border bg-white p-6 shadow-sm">
          {!detail ? (
            <p className="text-sm text-slate-500">Select a resume to view extracted text.</p>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold text-slate-900">{detail.filename}</h2>
                  <p className="text-sm text-slate-500">
                    Parser: {detail.parsed_resume?.parser_version ?? '—'}
                  </p>
                </div>
                <StatusBadge status={detail.status} />
              </div>

              {detail.status === 'failed' && (
                <p className="text-sm text-slate-600">
                  Parsing failed. Upload the resume again or choose another file.
                </p>
              )}

              {(detail.status === 'pending' || detail.status === 'parsing') && (
                <p className="text-sm text-slate-500">
                  Extracting text and running Ollama structured extraction...
                </p>
              )}

              {detail.parsed_resume && detail.parsed_resume.skills.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">Skills</h3>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {detail.parsed_resume.skills.map((skill) => (
                      <span
                        key={skill}
                        className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {detail.parsed_resume && detail.parsed_resume.experience.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">Experience</h3>
                  <ul className="mt-2 space-y-3">
                    {detail.parsed_resume.experience.map((item) => (
                      <li key={`${item.company}-${item.title}`} className="rounded-lg bg-slate-50 p-3">
                        <p className="text-sm font-medium text-slate-900">
                          {item.title} · {item.company}
                        </p>
                        <p className="text-xs text-slate-500">
                          {[item.start_date, item.end_date ?? 'Present'].filter(Boolean).join(' – ')}
                        </p>
                        {item.description && (
                          <p className="mt-1 text-sm text-slate-600">{item.description}</p>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {detail.parsed_resume && detail.parsed_resume.projects.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">Projects</h3>
                  <ul className="mt-2 space-y-3">
                    {detail.parsed_resume.projects.map((project) => (
                      <li key={project.name} className="rounded-lg bg-slate-50 p-3">
                        <p className="text-sm font-medium text-slate-900">{project.name}</p>
                        {project.description && (
                          <p className="mt-1 text-sm text-slate-600">{project.description}</p>
                        )}
                        {project.technologies.length > 0 && (
                          <p className="mt-2 text-xs text-slate-500">
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
                  <h3 className="text-sm font-semibold text-slate-900">Summary</h3>
                  <p className="mt-2 text-sm text-slate-600">{detail.parsed_resume.summary}</p>
                </div>
              )}

              {detail.parsed_resume?.raw_text && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">Extracted text</h3>
                  <pre className="mt-2 max-h-[32rem] overflow-auto whitespace-pre-wrap rounded-lg bg-slate-50 p-4 text-sm text-slate-700">
                    {detail.parsed_resume.raw_text}
                  </pre>
                </div>
              )}

              {detail.parsed_resume && (
                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="rounded-lg bg-slate-50 p-3">
                    <p className="text-xs uppercase text-slate-500">Name</p>
                    <p className="text-sm text-slate-900">{detail.parsed_resume.name ?? '—'}</p>
                  </div>
                  <div className="rounded-lg bg-slate-50 p-3">
                    <p className="text-xs uppercase text-slate-500">Email</p>
                    <p className="text-sm text-slate-900">{detail.parsed_resume.email ?? '—'}</p>
                  </div>
                  <div className="rounded-lg bg-slate-50 p-3">
                    <p className="text-xs uppercase text-slate-500">Phone</p>
                    <p className="text-sm text-slate-900">{detail.parsed_resume.phone ?? '—'}</p>
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
