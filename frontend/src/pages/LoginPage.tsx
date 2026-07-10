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
        <h1 className="text-2xl font-semibold text-slate-900">Sign in</h1>
        <p className="mt-1 text-sm text-slate-500">Access your AI Job Agent dashboard</p>
      </div>

      <form className="space-y-4" onSubmit={handleSubmit}>
        <div>
          <label htmlFor="email" className="mb-1 block text-sm font-medium text-slate-700">
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="w-full rounded-lg border border-surface-border px-3 py-2 text-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
            placeholder="you@example.com"
          />
        </div>
        <div>
          <label htmlFor="password" className="mb-1 block text-sm font-medium text-slate-700">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full rounded-lg border border-surface-border px-3 py-2 text-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
            placeholder="••••••••"
          />
        </div>
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
        >
          {isSubmitting ? 'Signing in...' : 'Sign in'}
        </button>
      </form>

      {showResendHint && (
        <p className="text-center text-sm text-slate-600">
          Need a new verification link?{' '}
          <button type="button" onClick={handleResend} className="font-medium text-brand-600 hover:text-brand-700">
            Resend email
          </button>
        </p>
      )}

      <p className="text-center text-sm text-slate-500">
        No account?{' '}
        <Link to="/register" className="font-medium text-brand-600 hover:text-brand-700">
          Create one
        </Link>
      </p>
    </div>
  )
}
