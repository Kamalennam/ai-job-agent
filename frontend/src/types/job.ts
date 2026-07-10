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
