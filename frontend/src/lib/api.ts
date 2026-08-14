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
  relationship?: string;
  linkedin_url?: string;
  github_url?: string;
  personal_url?: string;
  email?: string;
  source: string;
  overall_score: number;
  company_verified?: boolean;
  role_verified?: boolean;
  verification_confidence?: number;
  recommendation_reason?: string;
  selected?: boolean;
}

export type OutreachStateType =
  | "OFF"
  | "ENABLED"
  | "CHOOSING_CONTACT"
  | "DISCOVERING"
  | "CONTACT_SELECTED"
  | "DRAFTING"
  | "DRAFT_READY"
  | "SENT"
  | "FOLLOW_UP_AVAILABLE"
  | "FOLLOWED_UP";

export interface OutreachState {
  job_id: number;
  state: OutreachStateType;
  selected_contact?: Contact | null;
  channel: string;
  purpose: string;
  current_draft?: string | null;
  draft_subject?: string | null;
  draft_reasoning?: string | null;
  updated_at: string;
}

export interface OutreachEvent {
  id: number;
  job_id: number;
  contact_id: number;
  channel: string;
  subject?: string | null;
  message: string;
  sent_at: string;
  status: string;
  is_follow_up: boolean;
  sequence_number: number;
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

// --- OUTREACH MODULE API ---
export async function fetchOutreachState(jobId: number): Promise<OutreachState> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/outreach`);
  if (!res.ok) throw new Error("Failed to fetch outreach state");
  return res.json();
}

export async function enableOutreach(jobId: number): Promise<OutreachState> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/outreach/enable`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to enable outreach");
  return res.json();
}

export async function disableOutreach(jobId: number): Promise<OutreachState> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/outreach/disable`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to disable outreach");
  return res.json();
}

export async function fetchJobContacts(jobId: number): Promise<Contact[]> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/contacts`);
  if (!res.ok) throw new Error("Failed to fetch job contacts");
  return res.json();
}

export async function discoverContacts(jobId: number): Promise<Contact[]> {
  try {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/contacts/discover`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      throw new Error(`Failed to discover contacts (${res.status}): ${errText}`);
    }
    return await res.json();
  } catch (err) {
    console.error("Error in discoverContacts:", err);
    throw err;
  }
}

export async function findContactsForJob(jobId: number): Promise<{ job_id: number; contacts: Contact[] }> {
  const contacts = await discoverContacts(jobId);
  return { job_id: jobId, contacts };
}

export async function selectContact(jobId: number, contactId: number): Promise<OutreachState> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/contacts/select`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ contact_id: contactId }),
  });
  if (!res.ok) throw new Error("Failed to select contact");
  return res.json();
}

export async function importContact(payload: { name: string; company: string; title: string; profile_url?: string; email?: string; relationship?: string }): Promise<Contact> {
  const res = await fetch(`${API_BASE}/contacts/import`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to import contact");
  return res.json();
}

export async function fetchPersonalContacts(company?: string, query?: string): Promise<Contact[]> {
  const params = new URLSearchParams();
  if (company) params.append("company", company);
  if (query) params.append("query", query);
  
  const res = await fetch(`${API_BASE}/contacts?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch contacts");
  return res.json();
}

export async function generateOutreachDraft(
  jobId: number,
  contactId?: number,
  channel = "LinkedIn",
  purpose = "Introduce myself"
): Promise<OutreachState & { draft_message: string }> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/outreach/draft`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ contact_id: contactId, channel, purpose }),
  });
  if (!res.ok) throw new Error("Failed to generate outreach draft");
  const data: OutreachState = await res.json();
  return {
    ...data,
    draft_message: data.current_draft || "",
  };
}

export async function updateOutreachDraft(jobId: number, draft_message: string, subject?: string): Promise<OutreachState> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/outreach/draft`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ draft_message, subject }),
  });
  if (!res.ok) throw new Error("Failed to update outreach draft");
  return res.json();
}

export async function markOutreachSent(jobId: number, channel?: string): Promise<OutreachEvent> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/outreach/sent`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ channel }),
  });
  if (!res.ok) throw new Error("Failed to mark outreach sent");
  return res.json();
}

export async function generateFollowUpDraft(jobId: number, notes?: string): Promise<OutreachState> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/outreach/follow-up`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ notes }),
  });
  if (!res.ok) throw new Error("Failed to generate follow-up draft");
  return res.json();
}

export async function fetchOutreachEvents(jobId: number): Promise<OutreachEvent[]> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/outreach/events`);
  if (!res.ok) throw new Error("Failed to fetch outreach events");
  return res.json();
}

// --- STARTUPS API ---
export interface StartupContact {
  id: number;
  startup_id: number;
  name: string;
  title: string;
  persona_type: string;
  linkedin_url?: string;
  github_url?: string;
  email?: string;
  activity_score: number;
  activity_signals: string[];
  fit_score: number;
  created_at: string;
}

export interface StartupItem {
  id: number;
  name: string;
  domain?: string;
  company_size: string;
  funding_stage: string;
  summary?: string;
  tech_stack: string[];
  target_roles: string[];
  website_url?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  contacts: StartupContact[];
}

export interface StartupEnrichmentResponse {
  name: string;
  domain?: string;
  company_size: string;
  funding_stage: string;
  summary?: string;
  tech_stack: string[];
  target_roles: string[];
  website_url?: string;
}

export interface StartupDraftPitchResponse {
  contact_id: number;
  contact_name: string;
  contact_title: string;
  company_name: string;
  channel: string;
  purpose: string;
  subject?: string;
  draft_message: string;
  reasoning?: string;
}

export async function enrichStartup(domainOrName: string): Promise<StartupEnrichmentResponse> {
  const res = await fetch(`${API_BASE}/startups/enrich`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ domain_or_name: domainOrName }),
  });
  if (!res.ok) throw new Error("Failed to enrich startup");
  return res.json();
}

export async function createStartup(payload: Partial<StartupItem>): Promise<StartupItem> {
  const res = await fetch(`${API_BASE}/startups/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to create startup");
  return res.json();
}

export async function fetchStartups(): Promise<StartupItem[]> {
  const res = await fetch(`${API_BASE}/startups/`);
  if (!res.ok) throw new Error("Failed to fetch startups");
  return res.json();
}

export async function fetchStartupDetail(startupId: number): Promise<StartupItem> {
  const res = await fetch(`${API_BASE}/startups/${startupId}`);
  if (!res.ok) throw new Error("Failed to fetch startup detail");
  return res.json();
}

export async function discoverStartupContacts(startupId: number): Promise<StartupContact[]> {
  const res = await fetch(`${API_BASE}/startups/${startupId}/contacts/discover`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to discover startup contacts");
  return res.json();
}

export async function draftStartupPitch(contactId: number, channel = "LinkedIn", purpose = "Introduce myself"): Promise<StartupDraftPitchResponse> {
  const res = await fetch(`${API_BASE}/startups/contacts/${contactId}/draft`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ channel, purpose }),
  });
  if (!res.ok) throw new Error("Failed to draft startup pitch");
  return res.json();
}

export async function deleteStartup(startupId: number): Promise<void> {
  const res = await fetch(`${API_BASE}/startups/${startupId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete startup");
}


