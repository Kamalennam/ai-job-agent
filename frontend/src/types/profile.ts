export interface Profile {
  id: string
  email: string
  email_verified: boolean
  full_name: string
  headline: string | null
  location: string | null
  linkedin_url: string | null
  avatar_url: string | null
  bio: string | null
}

export interface UpdateProfileRequest {
  full_name: string
  headline: string | null
  location: string | null
  linkedin_url: string | null
  bio: string | null
}
