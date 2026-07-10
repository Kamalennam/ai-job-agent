import { api } from './api'
import type { Resume, ResumeDetail, ResumeListResponse } from '@/types/resume'

export const resumeService = {
  async upload(file: File, isPrimary = false): Promise<Resume> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('is_primary', String(isPrimary))

    const response = await api.post<Resume>('/resumes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  async list(): Promise<ResumeListResponse> {
    const response = await api.get<ResumeListResponse>('/resumes')
    return response.data
  },

  async get(resumeId: string): Promise<ResumeDetail> {
    const response = await api.get<ResumeDetail>(`/resumes/${resumeId}`)
    return response.data
  },
}
