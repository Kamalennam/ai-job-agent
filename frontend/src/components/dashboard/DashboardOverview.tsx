import { Link } from 'react-router-dom'
import { JobCard } from '@/components/jobs/JobCard'
import type { DashboardProfile, DashboardResponse } from '@/types/dashboard'
import type { Resume } from '@/types/resume'

const VISIBLE_SKILLS = 12

function StatusBadge({ status }: { status: Resume['status'] }) {
  const styles: Record<Resume['status'], string> = {
    pending: 'status-pending',
    parsing: 'status-parsing',
    parsed: 'status-parsed',
    failed: 'status-failed',
  }

  return <span className={styles[status]}>{status}</span>
}

function StatCard({
  label,
  value,
  detail,
  to,
}: {
  label: string
  value: number
  detail: string
  to: string
}) {
  return (
    <Link to={to} className="panel block p-4 transition-colors hover:border-[var(--color-brand)]">
      <p className="text-subtle text-xs font-medium uppercase tracking-wide">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
      <p className="text-muted mt-1 text-sm">{detail}</p>
    </Link>
  )
}

function ProfileSummary({ profile }: { profile: DashboardProfile }) {
  const skills = profile.skills.slice(0, VISIBLE_SKILLS)
  const hiddenSkills = profile.skills.length - skills.length
  const role = [profile.current_title, profile.current_company].filter(Boolean).join(' · ')

  return (
    <div className="panel p-6">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className="text-lg font-semibold">{profile.name || profile.filename}</h2>
          {role && <p className="text-muted mt-1 text-sm">{role}</p>}
          <p className="text-subtle mt-1 truncate text-sm">{profile.filename}</p>
        </div>
        <StatusBadge status={profile.status} />
      </div>

      {profile.summary && <p className="text-muted mt-4 line-clamp-4 text-sm">{profile.summary}</p>}

      {(profile.email || profile.phone) && (
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <div className="surface-muted-block">
            <p className="text-subtle text-xs uppercase">Email</p>
            <p className="mt-1 truncate text-sm">{profile.email ?? '—'}</p>
          </div>
          <div className="surface-muted-block">
            <p className="text-subtle text-xs uppercase">Phone</p>
            <p className="mt-1 text-sm">{profile.phone ?? '—'}</p>
          </div>
        </div>
      )}

      {skills.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-semibold">Skills</h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {skills.map((skill) => (
              <span key={skill} className="chip-brand">
                {skill}
              </span>
            ))}
            {hiddenSkills > 0 && <span className="text-subtle text-xs">+{hiddenSkills} more</span>}
          </div>
        </div>
      )}

      <Link to="/resumes" className="link-brand mt-4 inline-block">
        Open resumes
      </Link>
    </div>
  )
}

export function DashboardOverview({ data }: { data: DashboardResponse }) {
  const { overview, profile, recent_matches: matches, scoring } = data

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Resumes"
          value={overview.total_resumes}
          detail="Uploaded"
          to="/resumes"
        />
        <StatCard
          label="Parsed"
          value={overview.parsed_resumes}
          detail="Ready to match"
          to="/resumes"
        />
        <StatCard label="Jobs" value={overview.total_jobs} detail="Collected" to="/jobs" />
        <StatCard
          label="Matches"
          value={overview.total_matches}
          detail={scoring ? 'Scores updating' : 'For this profile'}
          to="/jobs"
        />
      </div>

      {profile ? (
        <ProfileSummary profile={profile} />
      ) : (
        <div className="panel-dashed p-8 text-center">
          <p className="text-muted text-sm">Upload a resume to see your profile here.</p>
          <Link to="/resumes" className="link-brand mt-3 inline-block">
            Go to resumes
          </Link>
        </div>
      )}

      <section className="space-y-4">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold">Strongest matches</h2>
          <Link to="/jobs" className="link-brand">
            View all
          </Link>
        </div>
        {matches.length === 0 ? (
          <div className="panel-dashed p-8 text-center">
            <p className="text-muted text-sm">
              {scoring ? 'Matching jobs for this resume…' : 'No matches yet.'}
            </p>
            <p className="text-subtle mt-1 text-sm">
              {scoring
                ? 'Scores are being saved. This page will update on its own.'
                : 'Collect jobs after a resume finishes parsing.'}
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {matches.map((job) => (
              <JobCard
                key={job.job_id}
                job={{
                  id: job.job_id,
                  title: job.title,
                  company: job.company,
                  location: job.location,
                  remote: job.remote,
                  posted_at: job.posted_at,
                  match_score: job.match_score,
                  matched_skills: job.matched_skills,
                  missing_skills: job.missing_skills,
                  match_reasons: job.match_reasons,
                }}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
