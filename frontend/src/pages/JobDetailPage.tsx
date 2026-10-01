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
        <Link to="/jobs" className="link-brand">
          ← Back to jobs
        </Link>
        <p className="text-muted text-sm">This job could not be loaded.</p>
      </div>
    )
  }

  if (!job) {
    return <p className="text-muted text-sm">Loading job...</p>
  }

  return (
    <div className="space-y-6">
      <Link to="/jobs" className="link-brand">
        ← Back to jobs
      </Link>

      <div className="panel p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="page-title">{job.title}</h1>
            <p className="text-muted mt-1 text-sm">
              {job.company}
              {job.location ? ` · ${job.location}` : ''}
            </p>
            {job.department && <p className="text-subtle mt-1 text-sm">Department: {job.department}</p>}
          </div>
          {job.remote && <span className="badge-success self-start">Remote</span>}
        </div>

        <div className="mt-4 flex flex-wrap gap-3">
          <a href={job.apply_url} target="_blank" rel="noreferrer" className="btn-primary">
            Apply on Greenhouse
          </a>
          {job.source_url && (
            <a href={job.source_url} target="_blank" rel="noreferrer" className="btn-secondary">
              View posting
            </a>
          )}
        </div>

        <div className="mt-6">
          <h2 className="text-sm font-semibold">Description</h2>
          <div className="text-muted mt-2 max-w-none whitespace-pre-wrap text-sm">{job.description}</div>
        </div>
      </div>
    </div>
  )
}
