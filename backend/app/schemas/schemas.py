import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

# Profile Schemas
class CandidateProfileBase(BaseModel):
    name: str = "Sam"
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    
    education: Dict[str, Any] = Field(default_factory=dict)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    skills: Dict[str, int] = Field(default_factory=dict) # e.g. {"Python": 8, "Machine Learning": 8}
    target_roles: List[str] = Field(default_factory=list)
    target_locations: List[str] = Field(default_factory=list)
    remote_preference: str = "Flexible"
    work_authorization: Dict[str, Any] = Field(default_factory=dict)
    preferred_industries: List[str] = Field(default_factory=list)
    excluded_companies: List[str] = Field(default_factory=list)
    salary_preferences: Dict[str, Any] = Field(default_factory=dict)
    resume_versions: Dict[str, Any] = Field(default_factory=dict)

class CandidateProfileCreate(CandidateProfileBase):
    pass

class CandidateProfileUpdate(CandidateProfileBase):
    pass

class CandidateProfileRead(CandidateProfileBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# Job Ingestion Schemas
class JobIngestRequest(BaseModel):
    url: Optional[str] = None
    job_description: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None

class JobAnalysisRead(BaseModel):
    id: int
    job_id: int
    technical_fit: int
    experience_fit: int
    education_fit: int
    location_fit: int
    authorization_fit: int
    career_alignment: int
    overall_score: int
    strengths: List[str]
    concerns: List[str]
    skill_gaps: List[str]
    resume_changes_needed: List[str]
    reasoning_summary: str
    model_name: str
    prompt_version: str
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class JobRead(BaseModel):
    id: int
    company: str
    title: str
    location: Optional[str] = None
    remote_type: Optional[str] = "Hybrid"
    employment_type: Optional[str] = "Full-time"
    description: str
    requirements: Optional[str] = None
    preferred_requirements: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    application_url: Optional[str] = None
    source_url: Optional[str] = None
    
    fit_score: Optional[int] = None
    priority: str = "B"
    recommendation: str = "APPLY"
    status: str = "Discovered"
    next_action: str = "Review Fit Analysis"
    next_action_at: Optional[datetime.datetime] = None
    fingerprint: str
    
    created_at: datetime.datetime
    updated_at: datetime.datetime
    
    analysis: Optional[JobAnalysisRead] = None
    model_config = ConfigDict(from_attributes=True)

class DecisionUpdateRequest(BaseModel):
    decision: str # "APPLY", "SAVE", "SKIP"
    notes: Optional[str] = None

# Contact Schemas
class ContactRead(BaseModel):
    id: int
    name: str
    company: str
    title: str
    team: Optional[str] = None
    relationship: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    personal_url: Optional[str] = None
    email: Optional[str] = None
    source: str
    overall_score: int
    company_verified: bool = True
    role_verified: bool = True
    verification_confidence: float = 0.9
    recommendation_reason: Optional[str] = None
    selected: bool = False
    model_config = ConfigDict(from_attributes=True)

class ContactImportRequest(BaseModel):
    name: str
    company: str
    title: str
    profile_url: Optional[str] = None
    email: Optional[str] = None
    relationship: Optional[str] = "Imported contact"

class ContactSelectRequest(BaseModel):
    contact_id: int

class FindContactsResponse(BaseModel):
    job_id: int
    contacts: List[ContactRead]

# Outreach Module Schemas
class OutreachToggleRequest(BaseModel):
    enabled: bool

class OutreachStateRead(BaseModel):
    job_id: int
    state: str # OFF, ENABLED, CHOOSING_CONTACT, DISCOVERING, CONTACT_SELECTED, DRAFTING, DRAFT_READY, SENT, FOLLOW_UP_AVAILABLE, FOLLOWED_UP
    selected_contact: Optional[ContactRead] = None
    channel: str = "LinkedIn"
    purpose: str = "Introduce myself"
    current_draft: Optional[str] = None
    draft_subject: Optional[str] = None
    draft_reasoning: Optional[str] = None
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class OutreachDraftRequest(BaseModel):
    contact_id: Optional[int] = None
    channel: str = "LinkedIn" # "LinkedIn", "Email", "Other"
    purpose: str = "Introduce myself" # "Introduce myself", "Ask about the team", "Ask for advice", "Ask for referral"

class OutreachDraftUpdateRequest(BaseModel):
    draft_message: str
    subject: Optional[str] = None

class OutreachDraftResponse(BaseModel):
    job_id: int
    contact_id: int
    channel: str
    purpose: str
    draft_message: str
    subject: Optional[str] = None
    reasoning: Optional[str] = None

class OutreachMarkSentRequest(BaseModel):
    channel: Optional[str] = None

class OutreachFollowUpRequest(BaseModel):
    notes: Optional[str] = None

class OutreachEventRead(BaseModel):
    id: int
    job_id: int
    contact_id: int
    channel: str
    subject: Optional[str] = None
    message: str
    sent_at: datetime.datetime
    status: str
    is_follow_up: bool
    sequence_number: int
    model_config = ConfigDict(from_attributes=True)

class OutreachContext(BaseModel):
    job_title: str
    company: str
    contact_name: str
    contact_title: str
    relationship: str = "Professional"
    relevant_user_experience: str = ""
    purpose: str = "Introduce myself"
    channel: str = "LinkedIn"

# Application Schemas
class ApplicationRead(BaseModel):
    id: int
    job_id: int
    status: str
    resume_version: Optional[str] = None
    applied_at: Optional[datetime.datetime] = None
    application_url: Optional[str] = None
    outreach_enabled: bool = False
    outreach_status: str = "OFF"
    notes: Optional[str] = None
    next_followup_at: Optional[datetime.datetime] = None
    model_config = ConfigDict(from_attributes=True)

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    resume_version: Optional[str] = None
    applied_at: Optional[datetime.datetime] = None
    outreach_enabled: Optional[bool] = None
    outreach_status: Optional[str] = None
    notes: Optional[str] = None

# Startup Schemas
class StartupEnrichRequest(BaseModel):
    domain_or_name: str

class StartupEnrichmentResponse(BaseModel):
    name: str
    domain: Optional[str] = None
    company_size: str = "1-15"
    funding_stage: str = "Seed"
    summary: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list)
    target_roles: List[str] = Field(default_factory=list)
    website_url: Optional[str] = None

class StartupCreate(BaseModel):
    name: str
    domain: Optional[str] = None
    company_size: str = "1-15"
    funding_stage: str = "Seed"
    summary: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list)
    target_roles: List[str] = Field(default_factory=list)
    website_url: Optional[str] = None
    notes: Optional[str] = None

class StartupContactRead(BaseModel):
    id: int
    startup_id: int
    name: str
    title: str
    persona_type: str = "ENG_LEAD"
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    email: Optional[str] = None
    activity_score: int = 75
    activity_signals: List[str] = Field(default_factory=list)
    fit_score: int = 80
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class StartupRead(BaseModel):
    id: int
    name: str
    domain: Optional[str] = None
    company_size: str
    funding_stage: str
    summary: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list)
    target_roles: List[str] = Field(default_factory=list)
    website_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    contacts: List[StartupContactRead] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

class StartupDraftPitchRequest(BaseModel):
    channel: str = "LinkedIn" # "LinkedIn", "Email", "Other"
    purpose: str = "Introduce myself"

class StartupDraftPitchResponse(BaseModel):
    contact_id: int
    contact_name: str
    contact_title: str
    company_name: str
    channel: str
    purpose: str
    subject: Optional[str] = None
    draft_message: str
    reasoning: Optional[str] = None


