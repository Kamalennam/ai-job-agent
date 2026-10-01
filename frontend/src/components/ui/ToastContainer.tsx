import { useToastStore } from '@/store/toastStore'

const styles: Record<string, string> = {
  success: 'panel toast-success',
  error: 'panel toast-error',
  info: 'panel toast-info',
}

export function ToastContainer() {
  const toasts = useToastStore((state) => state.toasts)
  const dismissToast = useToastStore((state) => state.dismissToast)

  if (toasts.length === 0) {
    return null
  }

  return (
    <div
      aria-live="polite"
      className="pointer-events-none fixed left-4 right-4 top-4 z-50 flex flex-col gap-2 sm:left-auto sm:right-4 sm:max-w-sm"
    >
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`pointer-events-auto px-4 py-3 text-sm ${styles[toast.type]}`}
          role="status"
        >
          <div className="flex items-start justify-between gap-3">
            <p className="font-medium">{toast.message}</p>
            <button
              type="button"
              onClick={() => dismissToast(toast.id)}
              className="text-subtle shrink-0 text-xs hover:opacity-100"
              aria-label="Dismiss notification"
            >
              ✕
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
