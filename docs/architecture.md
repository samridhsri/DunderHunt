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

---

## Architectural Decision Log

### Decision ADR-001: Expanded Candidate Profile Schema (Projects & Work Experience)
- **Date**: 2026-08-12
- **Context**: The V1 profile schema only tracked high-level skill dictionaries and target roles, causing LLM fit scoring to lack depth regarding prior work accomplishments and project portfolios.
- **Decision**: Added `projects` JSON column to `CandidateProfile` model and schema. Standardized `experience` and `projects` structures. Updated `JOB_FIT_PROMPT_TEMPLATE` (v2) to inject candidate work history and projects directly into Layer 2 LLM fit evaluation prompts.
- **Impact**: Fit Engine produces significantly more accurate technical alignment scores and identifies candidate strengths/concerns grounded in real project experience.
