import { Link } from 'react-router-dom'

interface JobCardModel {
  id: string
  title: string
  company: string
  location: string | null
  remote?: boolean | null
  posted_at?: string | null
  match_score?: number
  matched_skills?: string[]
  missing_skills?: string[]
  match_reasons?: string[]
}

interface JobCardProps {
  job: JobCardModel
}

export function JobCard({ job }: JobCardProps) {
  const matched = job.matched_skills ?? []
  const missing = job.missing_skills ?? []
  const reason = job.match_reasons?.[0]

  return (
    <Link to={`/jobs/${job.id}`} className="card-link">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold">{job.title}</h3>
          <p className="text-muted mt-1 text-sm">
            {job.company}
            {job.location ? ` · ${job.location}` : ''}
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {typeof job.match_score === 'number' && (
            <span className="badge-success">{job.match_score}% match</span>
          )}
          {job.remote && <span className="badge-success">Remote</span>}
        </div>
      </div>
      {matched.length > 0 && (
        <p className="text-muted mt-3 text-sm">Matched: {matched.slice(0, 6).join(', ')}</p>
      )}
      {missing.length > 0 && (
        <p className="text-subtle mt-1 text-sm">Missing: {missing.slice(0, 4).join(', ')}</p>
      )}
      {reason && <p className="text-subtle mt-2 text-xs">{reason}</p>}
      {job.posted_at && (
        <p className="text-subtle mt-2 text-xs">
          Posted {new Date(job.posted_at).toLocaleDateString()}
        </p>
      )}
    </Link>
  )
}
