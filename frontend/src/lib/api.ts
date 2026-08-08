const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface WorkExperience {
  id?: string;
  company: string;
  role: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  current?: boolean;
  description?: string;
  technologies?: string[];
}

export interface CandidateProject {
  id?: string;
  title: string;
  role?: string;
  url?: string;
  description?: string;
  technologies?: string[];
  highlights?: string[];
}

export interface CandidateProfile {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  education: Record<string, any>;
  experience: WorkExperience[];
  projects: CandidateProject[];
  skills: Record<string, number>;
  target_roles: string[];
  target_locations: string[];
  remote_preference: string;
  work_authorization: Record<string, any>;
  preferred_industries: string[];
  excluded_companies: string[];
  salary_preferences: Record<string, any>;
  resume_versions: Record<string, any>;
}

export interface JobAnalysis {
  id: number;
  job_id: number;
  technical_fit: number;
  experience_fit: number;
  education_fit: number;
  location_fit: number;
  authorization_fit: number;
  career_alignment: number;
  overall_score: number;
  strengths: string[];
  concerns: string[];
  skill_gaps: string[];
  resume_changes_needed: string[];
  reasoning_summary: string;
  model_name: string;
  prompt_version: string;
  created_at: string;
}

export interface JobItem {
  id: number;
  company: string;
  title: string;
  location?: string;
  remote_type?: string;
  employment_type?: string;
  description: string;
  requirements?: string;
  salary_min?: number;
  salary_max?: number;
  application_url?: string;
  source_url?: string;
  fit_score?: number;
  priority: 'A' | 'B' | 'C' | 'Skip';
  recommendation: 'APPLY' | 'SAVE' | 'SKIP';
  status: string;
  next_action: string;
  fingerprint: string;
  created_at: string;
  analysis?: JobAnalysis;
}

export interface Contact {
  id: number;
  name: string;
  company: string;
  title: string;
  team?: string;
  linkedin_url?: string;
  github_url?: string;
  email?: string;
  source: string;
  overall_score: number;
  recommendation_reason?: string;
  selected?: boolean;
}

export interface FindContactsResponse {
  job_id: number;
  contacts: Contact[];
}

export interface OutreachDraftResponse {
  job_id: number;
  contact_id: number;
  channel: string;
  purpose: string;
  draft_message: string;
}

export async function fetchProfile(): Promise<CandidateProfile> {
  const res = await fetch(`${API_BASE}/profile`);
  if (!res.ok) throw new Error("Failed to fetch profile");
  return res.json();
}

export async function updateProfile(data: Partial<CandidateProfile>): Promise<CandidateProfile> {
  const res = await fetch(`${API_BASE}/profile`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update profile");
  return res.json();
}

export async function fetchJobs(priority?: string, statusFilter?: string): Promise<JobItem[]> {
  const params = new URLSearchParams();
  if (priority) params.append("priority", priority);
  if (statusFilter) params.append("status_filter", statusFilter);
  
  const res = await fetch(`${API_BASE}/jobs?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch jobs");
  return res.json();
}

export async function fetchJobDetail(jobId: number): Promise<JobItem> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`);
  if (!res.ok) throw new Error("Failed to fetch job detail");
  return res.json();
}

export async function ingestJob(payload: { url?: string; job_description?: string; title?: string; company?: string; location?: string }): Promise<JobItem> {
  const res = await fetch(`${API_BASE}/jobs/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to ingest job");
  return res.json();
}

export async function updateJobDecision(jobId: number, decision: "APPLY" | "SAVE" | "SKIP", notes?: string): Promise<JobItem> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/decision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision, notes }),
  });
  if (!res.ok) throw new Error("Failed to update decision");
  return res.json();
}

export async function findContactsForJob(jobId: number): Promise<FindContactsResponse> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/find-contacts`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to find contacts");
  return res.json();
}

export async function generateOutreachDraft(jobId: number, contactId: number, channel = "LinkedIn", purpose = "Introduction"): Promise<OutreachDraftResponse> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/outreach`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ contact_id: contactId, channel, purpose }),
  });
  if (!res.ok) throw new Error("Failed to generate outreach draft");
  return res.json();
}
