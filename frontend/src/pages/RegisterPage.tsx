import { FormEvent, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { PasswordField } from '@/components/auth/PasswordField'
import { useAuthStore } from '@/store/authStore'
import { showSuccessToast } from '@/store/toastStore'
import { showApiErrorToast } from '@/utils/apiError'

export function RegisterPage() {
  const register = useAuthStore((state) => state.register)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSuccessMessage(null)
    setIsSubmitting(true)

    try {
      const response = await register({ email, password, full_name: fullName })
      showSuccessToast(response.message)
      setSuccessMessage(response.message)
    } catch (err) {
      showApiErrorToast(err, 'Registration failed. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (successMessage) {
    return (
      <div className="space-y-4 text-center">
        <h1 className="page-title">Check your email</h1>
        <p className="text-muted text-sm">{successMessage}</p>
        <p className="text-subtle text-sm">
          We sent a verification link to <span className="font-medium text-muted">{email}</span>.
        </p>
        <Link to="/login" className="btn-primary inline-block">
          Go to sign in
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Create account</h1>
        <p className="page-subtitle">Register to start using AI Job Agent</p>
      </div>

      <form className="space-y-4" onSubmit={handleSubmit}>
        <div>
          <label htmlFor="fullName" className="form-label">
            Full name
          </label>
          <input
            id="fullName"
            type="text"
            required
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
            className="input-field"
            placeholder="User Name"
          />
        </div>
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
          <PasswordField
            id="password"
            value={password}
            onChange={setPassword}
            placeholder="At least 8 characters"
            autoComplete="new-password"
            minLength={8}
          />
        </div>
        <button type="submit" disabled={isSubmitting} className="btn-primary w-full py-2.5">
          {isSubmitting ? 'Creating account...' : 'Create account'}
        </button>
      </form>

      <p className="text-muted text-center text-sm">
        Already have an account?{' '}
        <Link to="/login" className="link-brand">
          Sign in
        </Link>
      </p>
    </div>
  )
}
