export type JobSource = 'greenhouse'

export interface Job {
  id: string
  title: string
  company: string
  location: string | null
  source: JobSource
  remote: boolean | null
  posted_at: string | null
  apply_url: string
}

export interface JobDetail extends Job {
  description: string
  department: string | null
  employment_type: string | null
  source_url: string | null
  collected_at: string
}

export interface JobListResponse {
  items: Job[]
  total: number
  page: number
  page_size: number
}

export interface JobMatch {
  job_id: string
  title: string
  company: string
  location: string | null
  remote: boolean | null
  posted_at: string | null
  match_score: number
  matched_skills: string[]
  missing_skills: string[]
  matched_role: boolean
  experience_match: boolean
  project_matches: string[]
  match_reasons: string[]
  url: string
}

export interface JobMatchListResponse {
  resume_id: string
  total_jobs_analyzed: number
  total_matched_jobs: number
  page: number
  page_size: number
  jobs: JobMatch[]
}
