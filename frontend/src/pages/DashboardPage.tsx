import { useCallback, useEffect, useState } from 'react'
import { DashboardOverview } from '@/components/dashboard/DashboardOverview'
import { dashboardService } from '@/services/dashboardService'
import { showApiErrorToast } from '@/utils/apiError'
import type { DashboardResponse } from '@/types/dashboard'

const POLL_INTERVAL_MS = 2000

function isInProgress(data: DashboardResponse | null): boolean {
  if (!data) return false
  if (data.scoring) return true
  const status = data.profile?.status
  return status === 'pending' || status === 'parsing'
}

export function DashboardPage() {
  const [data, setData] = useState<DashboardResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const load = useCallback(async (silent = false) => {
    if (!silent) setIsLoading(true)
    try {
      const response = await dashboardService.get()
      setData(response)
    } catch (err) {
      if (!silent) showApiErrorToast(err, 'Could not load your overview.')
    } finally {
      if (!silent) setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  useEffect(() => {
    if (!isInProgress(data)) return
    const intervalId = window.setInterval(() => {
      void load(true)
    }, POLL_INTERVAL_MS)
    return () => window.clearInterval(intervalId)
  }, [data, load])

  const greeting = data?.profile?.name ? `Welcome, ${data.profile.name}` : 'Welcome'

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">{greeting}</h1>
        <p className="page-subtitle">Your resume, collected jobs, and strongest matches.</p>
      </div>
      {isLoading && !data ? (
        <p className="text-muted text-sm">Loading your overview...</p>
      ) : data ? (
        <DashboardOverview data={data} />
      ) : (
        <div className="panel-dashed p-8 text-center">
          <p className="text-muted text-sm">Your overview could not be loaded.</p>
        </div>
      )}
    </div>
  )
}
