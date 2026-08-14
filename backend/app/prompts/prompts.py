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

OUTREACH_DRAFT_PROMPT_TEMPLATE = """PROMPT_VERSION: outreach_v3


=== RECIPIENT ===
Contact Name: {contact_name}
Contact Title: {contact_title}
Company: {company}
Relationship: {relationship}
Contact Context: {contact_context}


=== OPPORTUNITY ===
Job Title: {job_title}
Job URL: {job_url}
Company Context: {company_context}
Outreach Purpose / Goal: {purpose}


=== CANDIDATE ===
Candidate Name: {candidate_name}
Relevant Experience: {relevant_user_experience}
Relevant Projects: {relevant_user_projects}
Key Differentiators: {candidate_differentiators}


=== CHANNEL ===
Channel: {channel}


=== OUTREACH STRATEGY ===

Your job is to write ONE highly targeted outreach message that maximizes the likelihood of getting a response.

Before writing, internally determine:

1. WHY THIS RECIPIENT?
   Identify the strongest reason this specific person is relevant to the candidate's goal.
   Examples:
   - They are the recruiter for the role.
   - They work directly on the relevant team.
   - They are the hiring manager.
   - They have a similar technical background.
   - They recently joined the company/team.
   - They posted about hiring.
   - They can provide a referral or internal context.

2. WHY THIS CANDIDATE?
   Select ONLY 1-2 experience points that directly connect the candidate to the recipient, team, company, or role.
   Do not dump the resume into the message.

3. WHAT IS THE ASK?
   Make the smallest reasonable ask for this relationship and purpose.
   Prefer:
   - Referral → politely ask whether they would be comfortable referring.
   - Recruiter → express interest and ask whether the profile could be considered.
   - Hiring manager → demonstrate fit and ask for a brief conversation or consideration.
   - Engineer/employee → ask for perspective or a referral only when appropriate.
   - Networking → ask a specific, easy-to-answer question.
   - Follow-up → reference the previous interaction and ask for the next step.

4. PERSONALIZATION
   Personalize using ONLY information explicitly provided in the input.
   Never invent:
   - shared experiences
   - mutual connections
   - projects
   - company knowledge
   - hiring responsibility
   - conversations
   - reasons for contacting them

5. MESSAGE QUALITY
   - Sound like a real candidate, not a marketing campaign.
   - Be direct, specific, and conversational.
   - Lead with relevance rather than flattery.
   - Give the recipient a clear reason to respond.
   - Keep the message focused on one objective.
   - Avoid unnecessary biography.
   - Avoid excessive enthusiasm.
   - Avoid asking multiple questions.
   - Never mention that the message was AI-generated.

6. CHANNEL RULES

   EMAIL:
   - Include a concise, specific subject line.
   - Use a professional but natural tone.
   - Keep the body concise.
   - Do not use "Dear".
   - A simple "Hi {contact_name}," is acceptable.
   - End with a low-friction CTA.

   LINKEDIN:
   - Be shorter and more conversational than email.
   - Do not include a formal subject line.
   - Optimize for a quick response.
   - Avoid sounding like a cover letter.

   LINKEDIN CONNECTION REQUEST:
   - Keep it extremely short.
   - Do not ask for a referral immediately unless the context strongly supports it.
   - Establish relevance first.

   X / TWITTER:
   - Be concise and natural.
   - Reference the relevant hiring post, role, or context when available.
   - Avoid corporate language.

   OTHER:
   - Follow the conventions of the specified channel.
   - Never blindly apply email conventions to another channel.

7. PURPOSE RULES
   Follow {purpose} exactly.
   Do not turn a networking message into a job application.
   Do not turn a referral request into a generic networking message.
   Do not ask for a referral if the recipient's relationship to the candidate does not justify it.
   Do not ask for a meeting when a simple question would be more appropriate.

8. LENGTH
   Maximum 120 words for email.
   For other channels, use the shortest length that can communicate:
   relevance → credibility → ask.

9. FINAL CHECK
   Before returning the message, internally verify:
   - Is this clearly written for THIS recipient?
   - Is there a concrete reason they should care?
   - Is the candidate's relevance obvious?
   - Is there exactly one primary CTA?
   - Is every factual claim supported by the provided context?
   - Does it sound human?
   - Could any sentence be removed without weakening the message?
   
   If yes, remove it.


=== OUTPUT ===

Return ONLY valid JSON matching OutreachDraftOutput.

If Channel is Email, include:
{{
  "subject": "...",
  "draft_message": "..."
}}

For non-email channels, omit the subject field.

Do not include analysis, reasoning, alternatives, markdown, or commentary."""

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

# Startup Enrichment Schemas & Prompts
class StartupEnrichmentOutput(BaseModel):
    name: str = Field(description="Normalized company name")
    company_size: str = Field(description="One of: '1-15', '15-50', '50-200', '200+'")
    funding_stage: str = Field(description="One of: 'Seed', 'Series A', 'Series B', 'Bootstrapped', 'Late Stage'")
    summary: str = Field(description="Concise 1-sentence company summary")
    tech_stack: List[str] = Field(description="Detected engineering tech stack keywords")
    target_roles: List[str] = Field(description="Relevant hiring role categories, e.g. Full Stack, AI Engineer")

STARTUP_ENRICHMENT_PROMPT_TEMPLATE = """PROMPT_VERSION: startup_enrichment_v1

Extract structured startup company details from the provided search snippets for domain/company '{domain_or_name}'.

Search Snippets:
{search_snippets}

Classify:
- company_size: Choose exactly one of ["1-15", "15-50", "50-200", "200+"]. If ambiguous, estimate based on funding or age. Default to "1-15" for early/stealth startups.
- funding_stage: Choose exactly one of ["Seed", "Series A", "Series B", "Bootstrapped", "Late Stage"].
- summary: Clear 1-sentence summary of what the startup builds.
- tech_stack: List of engineering technologies used (e.g. Python, FastAPI, React, PyTorch, Go, AWS).
- target_roles: List of likely hiring roles (e.g. Full Stack Engineer, AI/ML Engineer, Backend Engineer).

Return valid JSON matching StartupEnrichmentOutput schema."""

STARTUP_COLD_OUTREACH_PROMPT_TEMPLATE = """PROMPT_VERSION: startup_cold_outreach_v1

=== CANDIDATE PROFILE ===
Name: {candidate_name}
Target Roles: {target_roles}
Skills: {skills}
Top Projects: {projects}
Work Experience: {experience}

=== RECIPIENT ===
Contact Name: {contact_name}
Designation / Title: {contact_title}
Persona Category: {persona_type}
Company Name: {company_name}

=== STARTUP CONTEXT ===
Company Size: {company_size} ({funding_stage})
Tech Stack: {tech_stack}
Company Overview: {company_summary}

=== OUTREACH STRATEGY ===
Channel: {channel}
Purpose: {purpose}

Draft a personalized cold pitch from the candidate to this contact.

CRITICAL INSTRUCTIONS:
1. Relevancy First: Match the candidate's exact technical skills/projects to the startup's tech stack and mission.
2. Persona Tone:
   - If Founder/CTO: Focus on direct impact, fast execution, interest in building 0-to-1 product features.
   - If Eng Manager/Lead: Focus on technical stack alignment, system design, and specific project experience.
   - If Recruiter: Clear pitch of candidate background, key strengths, and current availability.
3. Message Style: Direct, conversational, zero fluff. No generic corporate buzzwords.
4. Channel Rules:
   - Email: Concise subject line + message under 120 words.
   - LinkedIn / Other: No subject line. Short conversational message under 90 words.
5. End with ONE clear, low-friction call to action (CTA).

Return JSON matching OutreachDraftOutput schema."""


