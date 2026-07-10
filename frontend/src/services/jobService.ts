import { api } from './api'
import type { JobDetail, JobListResponse } from '@/types/job'

export interface JobSearchParams {
  query?: string
  remote?: boolean
  page?: number
  page_size?: number
}

export const jobService = {
  async list(params: JobSearchParams = {}): Promise<JobListResponse> {
    const response = await api.get<JobListResponse>('/jobs', { params })
    return response.data
  },

  async get(jobId: string): Promise<JobDetail> {
    const response = await api.get<JobDetail>(`/jobs/${jobId}`)
    return response.data
  },

  async collect(): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/jobs/collect', {})
    return response.data
  },
}
