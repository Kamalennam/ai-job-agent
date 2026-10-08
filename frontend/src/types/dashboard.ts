import type { JobMatch } from '@/types/job'
import type { ResumeStatus } from '@/types/resume'

export interface DashboardOverview {
  total_resumes: number
  parsed_resumes: number
  total_jobs: number
  total_matches: number
}

export interface DashboardProfile {
  resume_id: string
  filename: string
  status: ResumeStatus
  is_primary: boolean
  name: string | null
  email: string | null
  phone: string | null
  summary: string | null
  skills: string[]
  current_title: string | null
  current_company: string | null
}

export interface DashboardResponse {
  overview: DashboardOverview
  profile: DashboardProfile | null
  recent_matches: JobMatch[]
  scoring: boolean
}
