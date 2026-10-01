import { FormEvent, useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import type { AxiosError } from 'axios'
import { useAuthStore } from '@/store/authStore'
import { showErrorToast, showSuccessToast } from '@/store/toastStore'
import type { ApiError } from '@/types/auth'
import { showApiErrorToast } from '@/utils/apiError'

export function LoginPage() {
  const navigate = useNavigate()
  const login = useAuthStore((state) => state.login)
  const resendVerification = useAuthStore((state) => state.resendVerification)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showResendHint, setShowResendHint] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setShowResendHint(false)
    setIsSubmitting(true)

    try {
      await login(email, password)
      showSuccessToast('Signed in successfully.')
      navigate('/dashboard')
    } catch (err) {
      showApiErrorToast(err, 'Sign in failed. Please try again.')
      const axiosError = err as AxiosError<ApiError>
      if (axiosError.response?.data?.error?.code === 'EMAIL_NOT_VERIFIED') {
        setShowResendHint(true)
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleResend = async () => {
    if (!email) {
      showErrorToast('Enter your email address to resend verification.')
      return
    }
    try {
      const message = await resendVerification(email)
      showSuccessToast(message)
    } catch (err) {
      showApiErrorToast(err, 'Could not resend verification email.')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Sign in</h1>
        <p className="page-subtitle">Access your AI Job Agent dashboard</p>
      </div>

      <form className="space-y-4" onSubmit={handleSubmit}>
        <div>
          <label htmlFor="email" className="form-label">
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="input-field"
            placeholder="you@example.com"
          />
        </div>
        <div>
          <label htmlFor="password" className="form-label">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="input-field"
            placeholder="••••••••"
          />
        </div>
        <button type="submit" disabled={isSubmitting} className="btn-primary w-full py-2.5">
          {isSubmitting ? 'Signing in...' : 'Sign in'}
        </button>
      </form>

      {showResendHint && (
        <p className="text-muted text-center text-sm">
          Need a new verification link?{' '}
          <button type="button" onClick={handleResend} className="link-brand">
            Resend email
          </button>
        </p>
      )}

      <p className="text-muted text-center text-sm">
        No account?{' '}
        <Link to="/register" className="link-brand">
          Create one
        </Link>
      </p>
    </div>
  )
}
