import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { ThemeToggle } from '@/components/layout/ThemeToggle'
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
    <div className="app-shell relative flex min-h-screen items-center justify-center px-4 py-8">
      <div className="absolute right-4 top-4 sm:right-6 sm:top-6">
        <ThemeToggle showLabel />
      </div>
      <div className="panel w-full max-w-md p-6 text-center sm:p-8">
        {status === 'loading' && <p className="text-muted text-sm">Verifying your email...</p>}

        {status === 'success' && (
          <div className="space-y-4">
            <h1 className="page-title">Email verified</h1>
            <p className="text-muted text-sm">Your email is verified. You can sign in now.</p>
            <Link to="/login" className="btn-primary inline-block">
              Sign in
            </Link>
          </div>
        )}

        {status === 'failed' && (
          <div className="space-y-4">
            <h1 className="page-title">Verification failed</h1>
            <p className="text-muted text-sm">
              We could not verify your email. Request a new link from the sign-in page.
            </p>
            <Link to="/login" className="btn-primary inline-block">
              Back to sign in
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
