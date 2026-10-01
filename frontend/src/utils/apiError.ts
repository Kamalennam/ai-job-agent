import type { AxiosError } from 'axios'
import type { ApiError } from '@/types/auth'
import { showErrorToast } from '@/store/toastStore'

/** User-safe messages only — never show raw server / stack / validation internals. */
const CLIENT_ERROR_MESSAGES: Record<string, string> = {
  DUPLICATE_EMAIL: 'An account with this email already exists.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  INTERNAL_ERROR: 'Something went wrong. Please try again later.',
  INVALID_CREDENTIALS: 'Invalid email or password.',
  UNAUTHORIZED: 'Invalid email or password.',
  EMAIL_NOT_VERIFIED: 'Please verify your email before signing in.',
  INVALID_TOKEN: 'This link is invalid or has expired.',
  TOKEN_EXPIRED: 'Your session has expired. Please sign in again.',
  FORBIDDEN: 'You do not have access to perform this action.',
  NOT_FOUND: 'The requested item could not be found.',
  INVALID_FILE_TYPE: 'Only PDF files are supported.',
  RESUME_REQUIRED: 'Select or upload a resume before matching jobs.',
  RESUME_NOT_PARSED: 'This resume is still parsing. Try again when parsing finishes.',
}

const STATUS_FALLBACKS: Record<number, string> = {
  400: 'Invalid request. Please check your input.',
  401: 'Please sign in to continue.',
  403: 'You do not have permission to do that.',
  404: 'The requested item could not be found.',
  409: 'This action conflicts with existing data.',
  422: 'Please check your input and try again.',
  500: 'Something went wrong. Please try again later.',
}

export function getApiErrorMessage(
  error: unknown,
  fallback = 'Something went wrong. Please try again.',
): string {
  const axiosError = error as AxiosError<ApiError>
  const apiError = axiosError.response?.data?.error
  const status = axiosError.response?.status

  if (apiError?.code && CLIENT_ERROR_MESSAGES[apiError.code]) {
    return CLIENT_ERROR_MESSAGES[apiError.code]
  }

  if (status && STATUS_FALLBACKS[status]) {
    return STATUS_FALLBACKS[status]
  }

  if (!axiosError.response) {
    return 'Unable to reach the server. Check your connection and try again.'
  }

  return fallback
}

export function showApiErrorToast(
  error: unknown,
  fallback = 'Something went wrong. Please try again.',
): void {
  showErrorToast(getApiErrorMessage(error, fallback))
}
