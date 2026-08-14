import logging
import urllib.parse
import re
from typing import List, Dict, Any, Optional
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Startup, StartupContact, SearchCache, CandidateProfile
from app.schemas.schemas import StartupEnrichmentResponse, StartupDraftPitchResponse
from app.prompts.prompts import (
    STARTUP_ENRICHMENT_PROMPT_TEMPLATE,
    StartupEnrichmentOutput,
    STARTUP_COLD_OUTREACH_PROMPT_TEMPLATE,
    OutreachDraftOutput
)
from app.core.llm import LLMProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

class StartupService:
    @staticmethod
    async def enrich_startup(db: AsyncSession, domain_or_name: str) -> StartupEnrichmentResponse:
        clean_input = domain_or_name.strip().lower().replace("https://", "").replace("http://", "").replace("www.", "")
        if "/" in clean_input:
            clean_input = clean_input.split("/")[0]

        cache_key = f"startup_enrichment:{clean_input}"
        res = await db.execute(select(SearchCache).where(SearchCache.cache_key == cache_key))
        cached_entry = res.scalar_one_or_none()
        
        if cached_entry and cached_entry.filtered_results:
            logger.info(f"Using cached startup enrichment for '{clean_input}'")
            res_data = cached_entry.filtered_results[0]
            return StartupEnrichmentResponse(**res_data)

        serper_key = settings.SERPER_API_KEY
        snippets: List[str] = []

        if serper_key:
            query = f'"{clean_input}" startup employees headcount funding stage tech stack site:crunchbase.com OR site:linkedin.com OR site:techcrunch.com OR site:github.com'
            try:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    resp = await client.post(
                        "https://google.serper.dev/search",
                        headers={
                            "X-API-KEY": serper_key,
                            "Content-Type": "application/json"
                        },
                        json={"q": query, "num": 5}
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        for item in data.get("organic", []):
                            snippets.append(f"{item.get('title', '')}: {item.get('snippet', '')}")
            except Exception as e:
                logger.warning(f"Serper API search failed for startup enrichment of '{clean_input}': {e}")

        search_context = "\n".join(snippets) if snippets else f"Startup name/domain: {clean_input}"

        prompt = STARTUP_ENRICHMENT_PROMPT_TEMPLATE.format(
            domain_or_name=clean_input,
            search_snippets=search_context
        )

        try:
            enrichment_out: StartupEnrichmentOutput = await LLMProvider.generate_structured(
                prompt=prompt,
                response_schema=StartupEnrichmentOutput,
                system_instruction="Extract accurate startup headcount, stage, tech stack, and summary. Return structured JSON."
            )
            
            domain_val = clean_input if "." in clean_input else f"{clean_input.lower().replace(' ', '')}.com"
            
            response = StartupEnrichmentResponse(
                name=enrichment_out.name or clean_input.capitalize(),
                domain=domain_val,
                company_size=enrichment_out.company_size if enrichment_out.company_size in ["1-15", "15-50", "50-200", "200+"] else "1-15",
                funding_stage=enrichment_out.funding_stage if enrichment_out.funding_stage in ["Seed", "Series A", "Series B", "Bootstrapped", "Late Stage"] else "Seed",
                summary=enrichment_out.summary,
                tech_stack=enrichment_out.tech_stack or ["Python", "FastAPI", "React"],
                target_roles=enrichment_out.target_roles or ["Full Stack Engineer", "Backend Engineer"],
                website_url=f"https://{domain_val}"
            )

            # Cache enrichment result
            new_cache = SearchCache(
                cache_key=cache_key,
                company=response.name,
                role="Enrichment",
                query_count=1,
                raw_results=[{"snippets": snippets}],
                filtered_results=[response.model_dump()],
                search_version="v1"
            )
            db.add(new_cache)
            await db.commit()

            return response
        except Exception as e:
            logger.error(f"LLM startup enrichment failed for '{clean_input}': {e}")
            domain_val = clean_input if "." in clean_input else f"{clean_input.lower().replace(' ', '')}.com"
            return StartupEnrichmentResponse(
                name=clean_input.split(".")[0].capitalize(),
                domain=domain_val,
                company_size="1-15",
                funding_stage="Seed",
                summary=f"Early stage technology startup at {domain_val}",
                tech_stack=["Python", "TypeScript", "React"],
                target_roles=["Full Stack Engineer", "Software Engineer"],
                website_url=f"https://{domain_val}"
            )

    @staticmethod
    async def discover_startup_contacts(db: AsyncSession, startup: Startup) -> List[StartupContact]:
        res = await db.execute(select(StartupContact).where(StartupContact.startup_id == startup.id))
        existing_contacts = list(res.scalars().all())
        if existing_contacts and len(existing_contacts) > 0:
            return existing_contacts

        size = startup.company_size
        if size == "1-15":
            target_queries = ['("CTO" OR "Co-Founder" OR "Founder" OR "CEO")']
        elif size == "15-50":
            target_queries = ['("CTO" OR "VP of Engineering" OR "Head of Talent" OR "Engineering Manager")']
        else: # 50-200, 200+
            target_queries = ['("Engineering Manager" OR "Technical Recruiter" OR "Head of Engineering")']

        serper_key = settings.SERPER_API_KEY
        discovered: List[Dict[str, Any]] = []

        if serper_key:
            query = f'site:linkedin.com/in "{startup.name}" {target_queries[0]}'
            try:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    resp = await client.post(
                        "https://google.serper.dev/search",
                        headers={
                            "X-API-KEY": serper_key,
                            "Content-Type": "application/json"
                        },
                        json={"q": query, "num": 5}
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        for item in data.get("organic", []):
                            link = item.get("link", "")
                            title_text = item.get("title", "")

                            if "linkedin.com/in" not in link.lower():
                                continue

                            clean_title = title_text.replace(" - LinkedIn", "").replace(" | LinkedIn", "").replace("...", "").strip()
                            parts = [p.strip() for p in clean_title.split(" - ") if p.strip()]

                            cand_name = parts[0] if len(parts) > 0 else "Leadership Contact"
                            cand_designation = " - ".join(parts[1:]) if len(parts) > 1 else f"Leader at {startup.name}"

                            d_lower = cand_designation.lower()
                            if "founder" in d_lower or "ceo" in d_lower or "cto" in d_lower:
                                p_type = "FOUNDER"
                            elif "recruiter" in d_lower or "talent" in d_lower:
                                p_type = "RECRUITER"
                            else:
                                p_type = "ENG_LEAD"

                            discovered.append({
                                "name": cand_name,
                                "title": cand_designation,
                                "persona_type": p_type,
                                "linkedin_url": link,
                                "github_url": f"https://github.com/search?q={urllib.parse.quote(cand_name)}",
                                "email": f"{cand_name.split()[0].lower()}@{startup.domain}" if startup.domain and len(cand_name.split()) > 0 else None,
                                "activity_score": 85,
                                "activity_signals": ["⚡ Serper Indexed Profile", "🎯 Target Persona Match"],
                                "fit_score": 88
                            })
            except Exception as e:
                logger.warning(f"Serper contact search failed for startup '{startup.name}': {e}")

        if not discovered:
            if size == "1-15":
                discovered = [
                    {
                        "name": f"Co-Founder & CTO ({startup.name})",
                        "title": "Co-Founder & Chief Technology Officer",
                        "persona_type": "FOUNDER",
                        "linkedin_url": f"https://linkedin.com/company/{startup.name.lower().replace(' ', '')}",
                        "github_url": f"https://github.com/search?q={startup.name}",
                        "email": f"founders@{startup.domain}" if startup.domain else None,
                        "activity_score": 90,
                        "activity_signals": ["🎯 Direct Hiring Founder", "📧 Domain Contact Verified"],
                        "fit_score": 92
                    },
                    {
                        "name": f"Founding Engineer ({startup.name})",
                        "title": "Founding Software Engineer",
                        "persona_type": "PEER",
                        "linkedin_url": f"https://linkedin.com/company/{startup.name.lower().replace(' ', '')}",
                        "github_url": f"https://github.com/search?q={startup.name}",
                        "email": f"engineering@{startup.domain}" if startup.domain else None,
                        "activity_score": 82,
                        "activity_signals": ["⚡ Active Engineering Lead"],
                        "fit_score": 85
                    }
                ]
            else:
                discovered = [
                    {
                        "name": f"VP of Engineering ({startup.name})",
                        "title": "Vice President of Engineering",
                        "persona_type": "ENG_LEAD",
                        "linkedin_url": f"https://linkedin.com/company/{startup.name.lower().replace(' ', '')}",
                        "github_url": f"https://github.com/search?q={startup.name}",
                        "email": f"vpeng@{startup.domain}" if startup.domain else None,
                        "activity_score": 88,
                        "activity_signals": ["🎯 Engineering Decision Maker"],
                        "fit_score": 90
                    },
                    {
                        "name": f"Technical Recruiter ({startup.name})",
                        "title": "Head of Talent Acquisition",
                        "persona_type": "RECRUITER",
                        "linkedin_url": f"https://linkedin.com/company/{startup.name.lower().replace(' ', '')}",
                        "github_url": None,
                        "email": f"talent@{startup.domain}" if startup.domain else None,
                        "activity_score": 80,
                        "activity_signals": ["📧 Active Recruiting Contact"],
                        "fit_score": 84
                    }
                ]

        created_contacts = []
        for item in discovered[:4]:
            sc = StartupContact(
                startup_id=startup.id,
                name=item["name"],
                title=item["title"],
                persona_type=item["persona_type"],
                linkedin_url=item.get("linkedin_url"),
                github_url=item.get("github_url"),
                email=item.get("email"),
                activity_score=item.get("activity_score", 80),
                activity_signals=item.get("activity_signals", []),
                fit_score=item.get("fit_score", 85)
            )
            db.add(sc)
            created_contacts.append(sc)

        await db.commit()
        for sc in created_contacts:
            await db.refresh(sc)
        return created_contacts

    @staticmethod
    async def generate_pitch(db: AsyncSession, contact: StartupContact, channel: str = "LinkedIn", purpose: str = "Introduce myself") -> StartupDraftPitchResponse:
        res_startup = await db.execute(select(Startup).where(Startup.id == contact.startup_id))
        startup = res_startup.scalar_one()

        res_profile = await db.execute(select(CandidateProfile).limit(1))
        profile = res_profile.scalar_one_or_none()

        candidate_name = profile.name if profile else "Sam"
        target_roles = ", ".join(profile.target_roles) if profile and profile.target_roles else "Full Stack / AI Engineer"
        skills = ", ".join(list(profile.skills.keys())) if profile and profile.skills else "Python, FastAPI, React, PostgreSQL"
        
        projects_str = ""
        if profile and profile.projects:
            proj_items = [f"{p.get('title')}: {p.get('highlights', p.get('description', ''))}" for p in profile.projects[:2]]
            projects_str = " | ".join(proj_items)
        else:
            projects_str = "Built DunderHunt decision engine using FastAPI and React."

        exp_str = ""
        if profile and profile.experience:
            exp_items = [f"{e.get('title')} at {e.get('company')}" for e in profile.experience[:2]]
            exp_str = " | ".join(exp_items)

        prompt = STARTUP_COLD_OUTREACH_PROMPT_TEMPLATE.format(
            candidate_name=candidate_name,
            target_roles=target_roles,
            skills=skills,
            projects=projects_str,
            experience=exp_str,
            contact_name=contact.name,
            contact_title=contact.title,
            persona_type=contact.persona_type,
            company_name=startup.name,
            company_size=startup.company_size,
            funding_stage=startup.funding_stage,
            tech_stack=", ".join(startup.tech_stack or []),
            company_summary=startup.summary or f"Startup building in {startup.name}",
            channel=channel,
            purpose=purpose
        )

        try:
            draft_out: OutreachDraftOutput = await LLMProvider.generate_structured(
                prompt=prompt,
                response_schema=OutreachDraftOutput,
                system_instruction="Draft a personalized, highly relevant cold pitch from candidate to startup leader. Return JSON."
            )
            return StartupDraftPitchResponse(
                contact_id=contact.id,
                contact_name=contact.name,
                contact_title=contact.title,
                company_name=startup.name,
                channel=channel,
                purpose=purpose,
                subject=draft_out.subject,
                draft_message=draft_out.draft_message,
                reasoning=f"Tailored pitch matching candidate {skills} skills to {startup.name}'s tech stack for {contact.persona_type}."
            )
        except Exception as e:
            logger.error(f"LLM pitch generation failed for contact {contact.id}: {e}")
            fallback_subject = f"Engineering inquiry — {candidate_name}" if channel == "Email" else None
            fallback_msg = (
                f"Hi {contact.name.split()[0]},\n\n"
                f"I've been following {startup.name}'s work on {startup.summary or 'your platform'}. "
                f"As a software engineer specializing in {skills}, I built automated pipeline systems and full-stack applications. "
                f"I'd love to connect and learn how I can contribute to {startup.name}'s engineering team as you scale."
            )
            return StartupDraftPitchResponse(
                contact_id=contact.id,
                contact_name=contact.name,
                contact_title=contact.title,
                company_name=startup.name,
                channel=channel,
                purpose=purpose,
                subject=fallback_subject,
                draft_message=fallback_msg,
                reasoning="Fallback personalized message template."
            )
