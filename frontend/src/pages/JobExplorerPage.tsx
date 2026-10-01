import { FormEvent, useCallback, useEffect, useState } from 'react'
import { JobCard } from '@/components/jobs/JobCard'
import { jobService } from '@/services/jobService'
import { resumeService } from '@/services/resumeService'
import { showSuccessToast } from '@/store/toastStore'
import { showApiErrorToast } from '@/utils/apiError'
import type { JobMatch } from '@/types/job'
import type { Resume } from '@/types/resume'

const PAGE_SIZE = 20

export function JobExplorerPage() {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [resumeId, setResumeId] = useState('')
  const [jobs, setJobs] = useState<JobMatch[]>([])
  const [totalMatched, setTotalMatched] = useState(0)
  const [totalAnalyzed, setTotalAnalyzed] = useState(0)
  const [page, setPage] = useState(1)
  const [query, setQuery] = useState('')
  const [appliedQuery, setAppliedQuery] = useState('')
  const [remoteOnly, setRemoteOnly] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [resumesLoaded, setResumesLoaded] = useState(false)
  const [isCollecting, setIsCollecting] = useState(false)

  const parsedResumes = resumes.filter((item) => item.status === 'parsed')
  const selectedResume = parsedResumes.find((item) => item.id === resumeId)

  useEffect(() => {
    void resumeService
      .list()
      .then((response) => {
        setResumes(response.items)
        const parsed = response.items.filter((item) => item.status === 'parsed')
        const initial = parsed.find((item) => item.is_primary) ?? parsed[0]
        setResumeId(initial?.id ?? '')
      })
      .catch((err) => {
        showApiErrorToast(err, 'Could not load resumes.')
      })
      .finally(() => setResumesLoaded(true))
  }, [])

  const loadJobs = useCallback(async () => {
    if (!resumeId) {
      setJobs([])
      setTotalMatched(0)
      setTotalAnalyzed(0)
      setIsLoading(false)
      return
    }
    setIsLoading(true)
    try {
      const response = await jobService.matches({
        resume_id: resumeId,
        query: appliedQuery || undefined,
        remote: remoteOnly ? true : undefined,
        page,
        page_size: PAGE_SIZE,
      })
      setJobs(response.jobs)
      setTotalMatched(response.total_matched_jobs)
      setTotalAnalyzed(response.total_jobs_analyzed)
    } catch (err) {
      setJobs([])
      showApiErrorToast(err, 'Could not load matching jobs.')
    } finally {
      setIsLoading(false)
    }
  }, [appliedQuery, page, remoteOnly, resumeId])

  useEffect(() => {
    if (!resumesLoaded) return
    void loadJobs()
  }, [loadJobs, resumesLoaded])

  const handleSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setPage(1)
    setAppliedQuery(query)
  }

  const handleResumeChange = (nextResumeId: string) => {
    setPage(1)
    setResumeId(nextResumeId)
  }

  const handleCollect = async () => {
    setIsCollecting(true)
    try {
      const response = await jobService.collect()
      showSuccessToast(`${response.message} Refreshing in a few seconds...`)
      window.setTimeout(() => {
        void loadJobs()
      }, 5000)
    } catch (err) {
      showApiErrorToast(err, 'Failed to start job collection.')
    } finally {
      setIsCollecting(false)
    }
  }

  const pageCount = Math.max(1, Math.ceil(totalMatched / PAGE_SIZE))
  const subtitle = selectedResume
    ? `${totalMatched} matches from ${totalAnalyzed} jobs for ${selectedResume.filename}`
    : 'Upload a parsed resume to see matching jobs'

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="page-title">Jobs</h1>
          <p className="page-subtitle">{subtitle}</p>
        </div>
        <button type="button" onClick={handleCollect} disabled={isCollecting} className="btn-primary">
          {isCollecting ? 'Collecting...' : 'Collect jobs now'}
        </button>
      </div>

      <form onSubmit={handleSearch} className="panel flex flex-col gap-3 p-4">
        <label className="text-muted text-sm" htmlFor="match-resume">
          Match against resume
        </label>
        <select
          id="match-resume"
          value={resumeId}
          onChange={(event) => handleResumeChange(event.target.value)}
          className="input-field"
          disabled={parsedResumes.length === 0}
        >
          {parsedResumes.length === 0 ? (
            <option value="">No parsed resume yet</option>
          ) : (
            parsedResumes.map((resume) => (
              <option key={resume.id} value={resume.id}>
                {resume.filename}
                {resume.is_primary ? ' (primary)' : ''}
              </option>
            ))
          )}
        </select>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Filter matched jobs by title, company, location..."
            className="input-field flex-1"
          />
          <label className="text-muted flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={remoteOnly}
              onChange={(event) => {
                setPage(1)
                setRemoteOnly(event.target.checked)
              }}
              className="input-checkbox"
            />
            Remote only
          </label>
          <button type="submit" className="btn-secondary">
            Search
          </button>
        </div>
      </form>

      {!resumesLoaded || isLoading ? (
        <p className="text-muted text-sm">Loading matching jobs...</p>
      ) : parsedResumes.length === 0 ? (
        <div className="panel-dashed p-8 text-center">
          <p className="text-muted text-sm">Select or upload a resume before matching jobs.</p>
          <p className="text-subtle mt-1 text-sm">
            Parsing must finish before a resume can be used for matching.
          </p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="panel-dashed p-8 text-center">
          <p className="text-muted text-sm">No jobs match this resume.</p>
          <p className="text-subtle mt-1 text-sm">
            {totalAnalyzed === 0
              ? 'Collect Greenhouse jobs, then match them against this resume.'
              : `${totalAnalyzed} jobs were scored and none reached the match threshold.`}
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {jobs.map((job) => (
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

      {parsedResumes.length > 0 && totalMatched > PAGE_SIZE && (
        <div className="flex items-center justify-between gap-3">
          <button
            type="button"
            className="btn-secondary"
            disabled={page <= 1 || isLoading}
            onClick={() => setPage((current) => Math.max(1, current - 1))}
          >
            Previous
          </button>
          <p className="text-muted text-sm">
            Page {page} of {pageCount}
          </p>
          <button
            type="button"
            className="btn-secondary"
            disabled={page >= pageCount || isLoading}
            onClick={() => setPage((current) => current + 1)}
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}
