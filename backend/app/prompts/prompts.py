from typing import List, Optional
from pydantic import BaseModel, Field

# Pydantic schemas for LLM structured output parsing

class JobFitOutput(BaseModel):
    technical_fit: int = Field(ge=0, le=100)
    experience_fit: int = Field(ge=0, le=100)
    education_fit: int = Field(ge=0, le=100)
    location_fit: int = Field(ge=0, le=100)
    authorization_fit: int = Field(ge=0, le=100)
    career_alignment: int = Field(ge=0, le=100)
    overall_score: int = Field(ge=0, le=100)
    priority: str = Field(description="Priority grade: A (90-100), B (80-89), C (70-79), or Skip (<70)")
    recommendation: str = Field(description="Action recommendation: APPLY, SAVE, or SKIP")
    strengths: List[str]
    concerns: List[str]
    skill_gaps: List[str]
    resume_changes_needed: List[str]
    reasoning_summary: str

class ContactItemSchema(BaseModel):
    name: str
    company: str
    title: str
    team: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    email: Optional[str] = None
    source: str
    overall_score: int
    recommendation_reason: str
    selected: bool = False

class ContactRankOutput(BaseModel):
    contacts: List[ContactItemSchema]

class OutreachDraftOutput(BaseModel):
    draft_message: str

# Versioned Prompts
JOB_FIT_SYSTEM_INSTRUCTION = """You are an expert technical career decision-support advisor.
Evaluate the given Job Description against the Candidate Profile strictly.
Output a JSON response matching the required schema. No fluff, no conversational greetings."""

JOB_FIT_PROMPT_TEMPLATE = """PROMPT_VERSION: job_fit_v2

=== CANDIDATE PROFILE ===
Name: {candidate_name}
Target Roles: {target_roles}
Target Locations: {target_locations}
Skills & Proficiency: {skills}
Work Authorization: {work_authorization}
Excluded Companies: {excluded_companies}

Work Experience:
{work_experience}

Projects & Portfolio:
{projects}

=== JOB POSTING ===
Company: {company}
Title: {title}
Location: {location}
Description:
{description}

Evaluate the fit score accurately according to the 7-component formula:
- Technical Fit (30%)
- Role Alignment (20%)
- Experience Level (15%)
- Work Authorization (15%)
- Location (10%)
- Career Value (5%)
- Application Effort (5%)

Provide concise JSON output."""

CONTACT_RANK_PROMPT_TEMPLATE = """PROMPT_VERSION: contact_rank_v1

=== TARGET JOB ===
Company: {company}
Title: {title}
Team/Function: {team}

=== CANDIDATE CONTACTS SURFACED FROM PUBLIC SEARCH ===
{candidates_json}

Evaluate and rank the top 3 contacts based on relevance, title match (Hiring Manager > Team Lead > Recruiter > Employee), and reachability.
Return strict JSON with the top 3 ranked contacts."""

OUTREACH_DRAFT_PROMPT_TEMPLATE = """PROMPT_VERSION: outreach_v1

=== RECIPIENT ===
Name: {contact_name}
Title: {contact_title}
Company: {company}

=== JOB & CANDIDATE ===
Job Title: {job_title}
Candidate Name: {candidate_name}
Channel: {channel}
Purpose: {purpose}

Draft ONE highly concise, professional message tailored to this channel and purpose. Keep it under 120 words. No boilerplate greetings or unnecessary AI fluff."""
