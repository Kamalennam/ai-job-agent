import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { jobService } from '@/services/jobService'
import { showApiErrorToast } from '@/utils/apiError'
import type { JobDetail } from '@/types/job'

export function JobDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [job, setJob] = useState<JobDetail | null>(null)
  const [loadFailed, setLoadFailed] = useState(false)

  useEffect(() => {
    if (!id) return
    void jobService
      .get(id)
      .then(setJob)
      .catch((err) => {
        setLoadFailed(true)
        showApiErrorToast(err, 'Could not load job details.')
      })
  }, [id])

  if (loadFailed) {
    return (
      <div className="space-y-4">
        <Link to="/jobs" className="text-sm font-medium text-brand-600 hover:text-brand-700">
          ← Back to jobs
        </Link>
        <p className="text-sm text-slate-600">This job could not be loaded.</p>
      </div>
    )
  }

  if (!job) {
    return <p className="text-sm text-slate-500">Loading job...</p>
  }

  return (
    <div className="space-y-6">
      <Link to="/jobs" className="text-sm font-medium text-brand-600 hover:text-brand-700">
        ← Back to jobs
      </Link>

      <div className="rounded-xl border border-surface-border bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">{job.title}</h1>
            <p className="mt-1 text-sm text-slate-600">
              {job.company}
              {job.location ? ` · ${job.location}` : ''}
            </p>
            {job.department && (
              <p className="mt-1 text-sm text-slate-500">Department: {job.department}</p>
            )}
          </div>
          {job.remote && (
            <span className="self-start rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-700">
              Remote
            </span>
          )}
        </div>

        <div className="mt-4 flex flex-wrap gap-3">
          <a
            href={job.apply_url}
            target="_blank"
            rel="noreferrer"
            className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
          >
            Apply on Greenhouse
          </a>
          {job.source_url && (
            <a
              href={job.source_url}
              target="_blank"
              rel="noreferrer"
              className="rounded-lg border border-surface-border px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              View posting
            </a>
          )}
        </div>

        <div className="mt-6">
          <h2 className="text-sm font-semibold text-slate-900">Description</h2>
          <div className="prose prose-sm mt-2 max-w-none whitespace-pre-wrap text-slate-700">
            {job.description}
          </div>
        </div>
      </div>
    </div>
  )
}
