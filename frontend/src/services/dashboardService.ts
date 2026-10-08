import { api } from './api'
import type { DashboardResponse } from '@/types/dashboard'

export const dashboardService = {
  async get(): Promise<DashboardResponse> {
    const response = await api.get<DashboardResponse>('/dashboard')
    return response.data
  },
}
