export type ResumeStatus = 'pending' | 'parsing' | 'parsed' | 'failed'

export interface Experience {
  company: string
  title: string
  start_date: string | null
  end_date: string | null
  description: string | null
  location: string | null
}

export interface Project {
  name: string
  description: string | null
  technologies: string[]
  url: string | null
  start_date: string | null
  end_date: string | null
}

export interface Resume {
  id: string
  filename: string
  file_url: string | null
  status: ResumeStatus
  is_primary: boolean
  created_at: string
}

export interface ParsedResume {
  id: string
  name: string | null
  email: string | null
  phone: string | null
  skills: string[]
  experience: Experience[]
  projects: Project[]
  summary: string | null
  raw_text: string | null
  parser_version: string
  parsed_at: string
}

export interface ResumeDetail extends Resume {
  parse_error: string | null
  parsed_resume: ParsedResume | null
}

export interface ResumeListResponse {
  items: Resume[]
  total: number
}
