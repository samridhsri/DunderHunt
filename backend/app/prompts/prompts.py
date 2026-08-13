from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

# Pydantic schemas for LLM structured output parsing

class JobFitOutput(BaseModel):
    technical_fit: int
    experience_fit: int
    education_fit: int
    location_fit: int
    authorization_fit: int
    career_alignment: int
    overall_score: int
    priority: str = Field(description="Priority grade: A (90-100), B (80-89), C (70-79), or Skip (<70)")
    recommendation: str = Field(description="Action recommendation: APPLY, SAVE, or SKIP")
    strengths: List[str]
    concerns: List[str]
    skill_gaps: List[str]
    resume_changes_needed: List[str]
    reasoning_summary: str

    @field_validator("technical_fit", "experience_fit", "education_fit", "location_fit", "authorization_fit", "career_alignment", "overall_score", mode="before")
    @classmethod
    def convert_score_to_int(cls, v):
        if isinstance(v, float):
            if v <= 10.0:
                return int(round(v * 10))
            return int(round(v))
        if isinstance(v, str):
            try:
                val = float(v)
                if val <= 10.0:
                    return int(round(val * 10))
                return int(round(val))
            except ValueError:
                return 75
        return v

class ContactItemSchema(BaseModel):
    name: str
    company: Optional[str] = None
    title: str
    team: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    email: Optional[str] = None
    source: str = "Public Search"
    overall_score: int = 85
    recommendation_reason: str = "Top match for role"
    selected: bool = False

class ContactRankOutput(BaseModel):
    contacts: List[ContactItemSchema]

class ExtractedPersonSchema(BaseModel):
    name: str
    title: str
    company: str
    profile_url: Optional[str] = None
    source_url: Optional[str] = None
    evidence: List[str] = Field(default_factory=list)

class CandidateExtractionOutput(BaseModel):
    people: List[ExtractedPersonSchema]

class OutreachDraftOutput(BaseModel):
    draft_message: str
    subject: Optional[str] = None
    reasoning: Optional[str] = None

class FollowUpDraftOutput(BaseModel):
    follow_up_message: str
    reasoning: Optional[str] = None

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

CANDIDATE_EXTRACTION_PROMPT_TEMPLATE = """PROMPT_VERSION: candidate_extract_v1

=== SEARCH PAGE CONTENT ===
Company: {company}
Role: {role}
Content Snippets:
{snippets}

Extract people and only facts explicitly supported by this content snippet.
Do NOT infer employment, team membership, or hiring manager responsibility without explicit text evidence.
Return strict JSON output with list of extracted people."""

CONTACT_RANK_PROMPT_TEMPLATE = """PROMPT_VERSION: contact_rank_v2

=== TARGET JOB ===
Company: {company}
Title: {title}
Team/Function: {team}

=== PRE-FILTERED CANDIDATES ===
{candidates_json}

Rank these candidates for relevance to this specific job.
Only use evidence provided. Do not infer employment, team membership, or hiring responsibility without evidence.
Assign a fit score (0-100) and concise recommendation reason for each candidate.
Return strict JSON output with the top 3 ranked contacts."""

OUTREACH_DRAFT_PROMPT_TEMPLATE = """PROMPT_VERSION: outreach_v2

=== RECIPIENT ===
Contact Name: {contact_name}
Contact Title: {contact_title}
Company: {company}
Relationship: {relationship}

=== JOB & CANDIDATE CONTEXT ===
Job Title: {job_title}
Candidate Name: {candidate_name}
Relevant Experience Highlights: {relevant_user_experience}
Channel: {channel}
Outreach Purpose / Goal: {purpose}

Write ONE concise, compelling outreach message tailored strictly to this channel and purpose.
If channel is Email, provide a short professional subject line.
Keep the draft under 120 words. Avoid generic greetings or AI clichés. Output structured JSON matching OutreachDraftOutput."""

FOLLOW_UP_DRAFT_PROMPT_TEMPLATE = """PROMPT_VERSION: follow_up_v1

=== RECIPIENT ===
Contact Name: {contact_name}
Title: {contact_title}
Company: {company}

=== PREVIOUS OUTREACH SENT ===
Channel: {channel}
Sent Date: {sent_at}
Original Message:
{previous_message}

=== FOLLOW-UP GOAL ===
Purpose: Polite follow-up after no response.
Additional Notes: {notes}

Draft ONE short, polite follow-up message (under 60 words) referencing the previous message. Output structured JSON matching FollowUpDraftOutput."""

