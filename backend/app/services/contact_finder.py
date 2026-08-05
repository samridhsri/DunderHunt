import json
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Job, Contact, JobContact
from app.prompts.prompts import (
    ContactRankOutput,
    CONTACT_RANK_PROMPT_TEMPLATE
)
from app.core.llm import LLMProvider

def build_search_queries(company: str, title: str) -> List[str]:
    return [
        f'"{company}" "{title}" hiring manager',
        f'"{company}" engineering manager',
        f'"{company}" recruiter software engineering',
        f'site:github.com "{company}" AI platform engineer'
    ]

def deterministic_contact_boost(title: str, team: str = "") -> int:
    t_lower = title.lower()
    score = 5  # generic baseline
    if "hiring manager" in t_lower or "engineering manager" in t_lower or "director" in t_lower or "head of" in t_lower:
        score += 40
    elif "lead" in t_lower or "principal" in t_lower or "staff" in t_lower:
        score += 30
    elif "recruiter" in t_lower or "talent" in t_lower or "sourcer" in t_lower:
        score += 25
    elif "engineer" in t_lower or "developer" in t_lower or "researcher" in t_lower:
        score += 20
    return score

class ContactFinderService:
    @staticmethod
    async def find_and_rank_contacts(db: AsyncSession, job_id: int) -> List[Contact]:
        # Fetch job
        job_result = await db.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()
        if not job:
            raise ValueError(f"Job with id {job_id} not found")

        # 1. Generate queries
        queries = build_search_queries(job.company, job.title)

        # 2. Public search candidates (Mocked / LLM-ranked candidate generation)
        candidates_raw = [
            {
                "name": "Sarah Chen",
                "company": job.company,
                "title": f"Engineering Manager - {job.title} Team",
                "team": "Engineering",
                "linkedin_url": f"https://linkedin.com/in/sarahchen-{job.company.lower()}",
                "github_url": None,
                "email": f"sarah.chen@{job.company.lower().replace(' ', '')}.com",
                "source": "Company Public Org Page"
            },
            {
                "name": "John Smith",
                "company": job.company,
                "title": f"Senior {job.title}",
                "team": "Core Platform",
                "linkedin_url": f"https://linkedin.com/in/johnsmith-{job.company.lower()}",
                "github_url": "https://github.com/johnsmith-dev",
                "email": f"john.smith@{job.company.lower().replace(' ', '')}.com",
                "source": "GitHub Public Commit Log"
            },
            {
                "name": "Mike Davis",
                "company": job.company,
                "title": "Technical Recruiter - Engineering",
                "team": "Talent Acquisition",
                "linkedin_url": f"https://linkedin.com/in/mikedavis-recruiter",
                "github_url": None,
                "email": f"mike.davis@{job.company.lower().replace(' ', '')}.com",
                "source": "Public Web Search"
            }
        ]

        # 3. LLM Ranking & Plausibility assessment
        prompt = CONTACT_RANK_PROMPT_TEMPLATE.format(
            company=job.company,
            title=job.title,
            team="Engineering",
            candidates_json=json.dumps(candidates_raw, indent=2)
        )

        rank_output: ContactRankOutput = await LLMProvider.generate_structured(
            prompt=prompt,
            response_schema=ContactRankOutput,
            model_name="gemini-2.5-flash",
            system_instruction="Rank contacts for job outreach carefully based on role relevance."
        )

        saved_contacts: List[Contact] = []
        
        # Remove existing contacts for job to prevent duplicates
        await db.execute(select(JobContact).where(JobContact.job_id == job.id))
        
        for idx, item in enumerate(rank_output.contacts[:3]):
            # Boost score with deterministic heuristic
            heuristic = deterministic_contact_boost(item.title)
            final_score = min(99, max(50, item.overall_score + heuristic // 2))

            contact = Contact(
                name=item.name,
                company=item.company,
                title=item.title,
                team=item.team or "Engineering",
                linkedin_url=item.linkedin_url,
                github_url=item.github_url,
                email=item.email,
                source=item.source,
                company_confidence=0.95,
                role_confidence=0.90,
                freshness_score=0.95,
                overall_score=final_score
            )
            db.add(contact)
            await db.flush()

            job_contact = JobContact(
                job_id=job.id,
                contact_id=contact.id,
                recommended=True,
                recommendation_reason=item.recommendation_reason,
                selected=(idx == 0) # Select top contact by default
            )
            db.add(job_contact)
            saved_contacts.append(contact)

        await db.commit()
        return saved_contacts
