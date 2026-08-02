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
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    personal_url: Optional[str] = None
    email: Optional[str] = None
    source: str
    overall_score: int
    recommendation_reason: Optional[str] = None
    selected: bool = False
    model_config = ConfigDict(from_attributes=True)

class FindContactsResponse(BaseModel):
    job_id: int
    contacts: List[ContactRead]

# Outreach Schemas
class OutreachDraftRequest(BaseModel):
    contact_id: int
    channel: str = "LinkedIn" # "LinkedIn", "Email", "Other"
    purpose: str = "Introduction" # "Introduction", "Ask about team", "Referral", "Role-specific question"

class OutreachDraftResponse(BaseModel):
    job_id: int
    contact_id: int
    channel: str
    purpose: str
    draft_message: str

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
