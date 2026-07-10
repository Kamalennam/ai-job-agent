import { create } from 'zustand'

export type ToastType = 'success' | 'error' | 'info'

export interface ToastItem {
  id: string
  message: string
  type: ToastType
}

interface ToastState {
  toasts: ToastItem[]
  showToast: (message: string, type?: ToastType) => void
  dismissToast: (id: string) => void
}

const AUTO_DISMISS_MS = 5000

export const useToastStore = create<ToastState>((set, get) => ({
  toasts: [],
  showToast: (message, type = 'info') => {
    const id = crypto.randomUUID()
    set((state) => ({
      toasts: [...state.toasts, { id, message, type }],
    }))

    window.setTimeout(() => {
      get().dismissToast(id)
    }, AUTO_DISMISS_MS)
  },
  dismissToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id),
    }))
  },
}))

export function showSuccessToast(message: string) {
  useToastStore.getState().showToast(message, 'success')
}

export function showErrorToast(message: string) {
  useToastStore.getState().showToast(message, 'error')
}

export function showInfoToast(message: string) {
  useToastStore.getState().showToast(message, 'info')
}
