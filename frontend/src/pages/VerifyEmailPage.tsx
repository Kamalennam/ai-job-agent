import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { authService } from '@/services/authService'
import { showErrorToast, showSuccessToast } from '@/store/toastStore'
import { showApiErrorToast } from '@/utils/apiError'

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const [status, setStatus] = useState<'loading' | 'success' | 'failed'>('loading')

  useEffect(() => {
    if (!token) {
      showErrorToast('Verification link is invalid.')
      setStatus('failed')
      return
    }

    let active = true

    void authService
      .verifyEmail(token)
      .then((response) => {
        if (!active) return
        showSuccessToast(response.message)
        setStatus('success')
      })
      .catch((err) => {
        if (!active) return
        showApiErrorToast(err, 'Email verification failed. The link may be invalid or expired.')
        setStatus('failed')
      })

    return () => {
      active = false
    }
  }, [token])

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-muted px-4">
      <div className="w-full max-w-md rounded-xl border border-surface-border bg-white p-8 text-center shadow-sm">
        {status === 'loading' && <p className="text-sm text-slate-500">Verifying your email...</p>}

        {status === 'success' && (
          <div className="space-y-4">
            <h1 className="text-2xl font-semibold text-slate-900">Email verified</h1>
            <p className="text-sm text-slate-600">Your email is verified. You can sign in now.</p>
            <Link
              to="/login"
              className="inline-block rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
            >
              Sign in
            </Link>
          </div>
        )}

        {status === 'failed' && (
          <div className="space-y-4">
            <h1 className="text-2xl font-semibold text-slate-900">Verification failed</h1>
            <p className="text-sm text-slate-600">
              We could not verify your email. Request a new link from the sign-in page.
            </p>
            <Link
              to="/login"
              className="inline-block rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
            >
              Back to sign in
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
