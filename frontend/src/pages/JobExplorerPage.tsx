import { FormEvent, useCallback, useEffect, useState } from 'react'
import { JobCard } from '@/components/jobs/JobCard'
import { jobService } from '@/services/jobService'
import { showSuccessToast } from '@/store/toastStore'
import { showApiErrorToast } from '@/utils/apiError'
import type { Job } from '@/types/job'

export function JobExplorerPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [total, setTotal] = useState(0)
  const [query, setQuery] = useState('')
  const [remoteOnly, setRemoteOnly] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [isCollecting, setIsCollecting] = useState(false)

  const loadJobs = useCallback(async () => {
    setIsLoading(true)
    try {
      const response = await jobService.list({
        query: query || undefined,
        remote: remoteOnly ? true : undefined,
        page: 1,
        page_size: 50,
      })
      setJobs(response.items)
      setTotal(response.total)
    } catch (err) {
      showApiErrorToast(err, 'Could not load jobs.')
    } finally {
      setIsLoading(false)
    }
  }, [query, remoteOnly])

  useEffect(() => {
    void loadJobs()
  }, [loadJobs])

  const handleSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    void loadJobs()
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

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Jobs</h1>
          <p className="mt-1 text-sm text-slate-500">
            Greenhouse listings collected into MongoDB ({total} active)
          </p>
        </div>
        <button
          type="button"
          onClick={handleCollect}
          disabled={isCollecting}
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
        >
          {isCollecting ? 'Collecting...' : 'Collect jobs now'}
        </button>
      </div>

      <form
        onSubmit={handleSearch}
        className="flex flex-col gap-3 rounded-xl border border-surface-border bg-white p-4 shadow-sm sm:flex-row sm:items-center"
      >
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search title, company, location..."
          className="flex-1 rounded-lg border border-surface-border px-3 py-2 text-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
        />
        <label className="flex items-center gap-2 text-sm text-slate-600">
          <input
            type="checkbox"
            checked={remoteOnly}
            onChange={(event) => setRemoteOnly(event.target.checked)}
            className="rounded border-surface-border text-brand-600 focus:ring-brand-500"
          />
          Remote only
        </label>
        <button
          type="submit"
          className="rounded-lg border border-surface-border px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Search
        </button>
      </form>

      {isLoading ? (
        <p className="text-sm text-slate-500">Loading jobs...</p>
      ) : jobs.length === 0 ? (
        <div className="rounded-xl border border-dashed border-surface-border bg-white p-8 text-center">
          <p className="text-sm text-slate-600">No jobs yet.</p>
          <p className="mt-1 text-sm text-slate-500">
            Click &quot;Collect jobs now&quot; to fetch Greenhouse listings.
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}
    </div>
  )
}
