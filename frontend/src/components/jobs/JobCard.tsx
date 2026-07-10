import { Link } from 'react-router-dom'
import type { Job } from '@/types/job'

interface JobCardProps {
  job: Job
}

export function JobCard({ job }: JobCardProps) {
  return (
    <Link
      to={`/jobs/${job.id}`}
      className="block rounded-xl border border-surface-border bg-white p-4 shadow-sm transition-colors hover:border-brand-200 hover:bg-brand-50/30"
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-slate-900">{job.title}</h3>
          <p className="mt-1 text-sm text-slate-600">
            {job.company}
            {job.location ? ` · ${job.location}` : ''}
          </p>
        </div>
        {job.remote && (
          <span className="rounded-full bg-green-50 px-2.5 py-0.5 text-xs font-medium text-green-700">
            Remote
          </span>
        )}
      </div>
      {job.posted_at && (
        <p className="mt-2 text-xs text-slate-500">
          Posted {new Date(job.posted_at).toLocaleDateString()}
        </p>
      )}
    </Link>
  )
}
