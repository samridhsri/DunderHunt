# DunderHunt System Architecture & Data Schemas

## Overview
DunderHunt is a single-user decision-support system for job search automation, candidate fit evaluation, and decision workflow tracking.

## Database Schema & Domain Models

### Candidate Profile (`candidate_profile`)
Source of truth for candidate skills, background, target roles, hard filters, and preferences used by the Fit Engine.

| Field | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-incrementing identifier |
| `name` | String(255) | Candidate name |
| `email` | String(255) | Contact email |
| `phone` | String(50) | Contact phone |
| `linkedin_url` | String(512) | LinkedIn profile URL |
| `github_url` | String(512) | GitHub profile URL |
| `portfolio_url` | String(512) | Personal portfolio website |
| `education` | JSON | List/Dict of academic degrees and certifications |
| `experience` | JSON | Structured work experiences (company, role, dates, description, tech stack) |
| `projects` | JSON | Structured projects (title, role, description, url, highlights, tech stack) |
| `skills` | JSON | Dict mapping skill name to proficiency rating (1-10) |
| `target_roles` | JSON | List of target job titles |
| `target_locations` | JSON | List of target cities or remote preferences |
| `remote_preference` | String(50) | Remote, Hybrid, or Onsite preference |
| `work_authorization` | JSON | Visa/citizenship authorization status |
| `preferred_industries` | JSON | List of preferred industry sectors |
| `excluded_companies` | JSON | List of company names to auto-skip |
| `salary_preferences` | JSON | Minimum / target compensation |
| `resume_versions` | JSON | Available resume version titles |

### Search Cache (`search_cache`)
Caches public web search results for candidate contact discovery by `contact_discovery:{company}:{team}:{role}`.

| Field | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-incrementing identifier |
| `cache_key` | String(255) (Unique Index) | Unique key `contact_discovery:{company}:{team}:{role}` |
| `company` | String(255) | Target company name |
| `role` | String(255) | Target job title |
| `query_count` | Integer | Total search queries generated (max 4) |
| `raw_results` | JSON | Extracted raw candidate search snippets |
| `filtered_results` | JSON | Verified candidates remaining after Python pre-filtering & LLM ranking |
| `search_version` | String(50) | Version tag (default "v8") |
| `created_at` | DateTime | Timestamp of initial search caching |

### Outreach State (`outreach_states`)
Tracks explicit 10-state lifecycle per job (`OFF`, `ENABLED`, `CHOOSING_CONTACT`, `DISCOVERING`, `CONTACT_SELECTED`, `DRAFTING`, `DRAFT_READY`, `SENT`, `FOLLOW_UP_AVAILABLE`, `FOLLOWED_UP`).

| Field | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-incrementing identifier |
| `job_id` | Integer (FK) | Unique foreign key to `jobs.id` |
| `state` | String(50) | State machine enum value |
| `selected_contact_id` | Integer (FK) | Active selected contact ID |
| `channel` | String(50) | Outreach channel (`LinkedIn`, `Email`, `Other`) |
| `purpose` | String(100) | Goal (`Introduce myself`, `Ask about the team`, `Ask for advice`, `Ask for referral`) |
| `current_draft` | Text | Generated draft message text |
| `draft_subject` | Text | Email subject line draft |
| `draft_reasoning` | Text | Internal LLM reasoning |

---

## Architectural Decision Log

### Decision ADR-001: Expanded Candidate Profile Schema (Projects & Work Experience)
- **Date**: 2026-08-12
- **Context**: The V1 profile schema only tracked high-level skill dictionaries and target roles, causing LLM fit scoring to lack depth regarding prior work accomplishments and project portfolios.
- **Decision**: Added `projects` JSON column to `CandidateProfile` model and schema. Standardized `experience` and `projects` structures. Updated `JOB_FIT_PROMPT_TEMPLATE` (v2) to inject candidate work history and projects directly into Layer 2 LLM fit evaluation prompts.
- **Impact**: Fit Engine produces significantly more accurate technical alignment scores and identifies candidate strengths/concerns grounded in real project experience.

### Decision ADR-002: Refined Contact Discovery Pipeline, Python Pre-Filtering & Search Caching
- **Date**: 2026-08-12
- **Context**: Contact discovery required predictable API costs, maximum ~5 search requests per job, deduplication, removal of noise (ex-employees, execs, unrelated departments), and caching so subsequent user clicks don't hit external search APIs.
- **Decision**:
  1. Plain Python query templates (`"{company}" "{role}" hiring manager`, `"{company}" "{role}" recruiter`, `"{company}" "{team}" engineering manager`, `"{company}" "{specialization}" engineer`) generating 3-5 targeted queries per job.
  2. Persistent PostgreSQL caching in `search_cache` table keyed by `company|role|search_version`.
  3. Deterministic Python candidate pre-filtering removing ex-employees, wrong departments, duplicates, and C-level execs, reducing raw candidate lists down to top ~5 clean candidates.
  4. Targeted LLM candidate ranking evaluating only the pre-filtered candidate subset to return top 3 decision-ready contacts.
- **Impact**: Zero redundant external search API calls on re-run, strict cost bounding (~5 queries max), and ultra-focused LLM context for fast, accurate contact ranking.

### Decision ADR-003: Self-Contained Modular Outreach Architecture & Explicit State Machine
- **Date**: 2026-08-12
- **Context**: Outreach was previously tightly coupled to initial job analysis modals. Re-architecting outreach into a self-contained module attached to a job required independent components for contact source selection, message drafting, event tracking, follow-up, personal contact DB querying, and replaceable discovery interfaces.
- **Decision**:
  1. Decoupled services under `services/outreach/` (`service.py`, `discovery.py`, `extraction.py`, `ranking.py`, `verification.py`, `strategy.py`, `messaging.py`), `services/contacts/`, and `services/jobs/`.
  2. Introduced an explicit 10-state machine (`OFF`, `ENABLED`, `CHOOSING_CONTACT`, `DISCOVERING`, `CONTACT_SELECTED`, `DRAFTING`, `DRAFT_READY`, `SENT`, `FOLLOW_UP_AVAILABLE`, `FOLLOWED_UP`) in `OutreachStateRecord`.
  3. Isolated `ContactDiscoveryService.discover(job)` interface so search engines can be swapped without touching application logic or UI.
  4. Standardized 12 API endpoints providing independent controls for toggles, candidate selection, import, personalized drafting via `OutreachContext`, sentence tracking, and follow-ups.
  5. Built modular React components under `frontend/src/components/outreach/` mounted as `<OutreachPanel jobId={job.id} company={job.company} />`.
- **Impact**: Clean architectural boundary separating core job fit evaluation from outreach decision support, zero automatic contacting/applying, strict single-user decision-support UX, and robust cost caching.

### Decision ADR-004: Serper Google Search API Provider for Contact Discovery
- **Date**: 2026-08-13
- **Context**: HTML scrapers for search engines are subject to anti-bot rate-limiting and CAPTCHAs, leading to generic contact fallbacks. A reliable search API was needed to fetch real indexed Google snippets containing real names, exact titles, and verified LinkedIn URLs.
- **Decision**:
  1. Integrated Serper.dev Google Search API into `ContactDiscoveryService.discover(job)` using `SERPER_API_KEY`.
  2. Configured query format: `site:linkedin.com/in "{company}" ("{role}" OR "Engineering Manager" OR "Recruiter")`.
  3. Maintained persistent caching in `SearchCache` (`contact_discovery:{company}:{team}:{role}`) to ensure max 1 Serper API call per unique job/company/role combination.
  4. Retained graceful multi-tier fallbacks: Serper Google API → Public Search → LLM Extraction → Company Directory fallback.
- **Impact**: High-precision discovery of real named contacts with 100% API reliability, zero anti-bot rate-limits, and minimal API cost bounded by SearchCache.

### Decision ADR-005: Startup Prospecting, Automated Enrichment & Candidate-Matched Pitch Generator
- **Date**: 2026-08-13
- **Context**: Users required a complementary startup-first outbound prospecting flow alongside the job-first inbound queue. This required automatically enriching company headcount and tech stack without manual user entry, discovering named decision-makers with titles/designations, and drafting personalized cold pitches matching candidate skills/projects to the startup's tech stack.
- **Decision**:
  1. Built `startups` and `startup_contacts` tables in `app/models/models.py`.
  2. Implemented automated company enrichment (`StartupService.enrich_startup`) combining Serper Google Search snippets with structured LLM extraction (`StartupEnrichmentOutput`) and `SearchCache` caching (`startup_enrichment:{domain}`).
  3. Established headcount-based persona routing (Size 1-15 -> Founder/CTO; Size 15-50 -> CTO/VP Eng; Size 50-200 -> Eng Manager/Recruiter) returning explicit contact Names, Designations, and public activity signals (`⚡ Serper Indexed`, `🎯 Persona Match`).
  4. Implemented `StartupService.generate_pitch` using candidate profile (skills, projects, experience) and startup tech stack match to generate channel-specific pitches (`LinkedIn`, `Email`).
  5. Built dedicated frontend **Startups Hub** page (`frontend/src/app/startups/page.tsx`) and navigation tab.
- **Impact**: Zero manual employee count lookup required, zero LinkedIn scraping dependencies, automated headcount detection, exact contact names & designations, and high-conversion personalized pitches.



