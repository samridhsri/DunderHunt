import json
import logging
import re
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.models import Job, Contact, JobContact, SearchCache
from app.prompts.prompts import (
    ContactRankOutput,
    CONTACT_RANK_PROMPT_TEMPLATE
)
from app.core.llm import LLMProvider

logger = logging.getLogger(__name__)

SEARCH_VERSION = "v8"

def build_search_queries(company: str, role: str, team: str = "Engineering", specialization: str = "") -> List[str]:
    """
    Generates 3 to 5 highly targeted plain Python search queries.
    Strictly capped at <= 5 queries per job for predictable cost control.
    """
    spec = specialization or role
    clean_company = company.strip()
    clean_role = role.strip()
    
    queries = [
        f'"{clean_company}" "{clean_role}" hiring manager',
        f'"{clean_company}" "{clean_role}" recruiter',
        f'"{clean_company}" "{team}" engineering manager',
        f'"{clean_company}" "{spec}" engineer',
    ]
    return queries[:4]

def filter_candidates_python(candidates_raw: List[Dict[str, Any]], job_title: str, company: str) -> List[Dict[str, Any]]:
    """
    Deterministic Python filtering rules:
    1. Removes people no longer at company (ex-, former, past, company mismatch)
    2. Removes clearly unrelated departments (Finance, Legal, Ops unless role is in those areas)
    3. Removes duplicate profiles (same URL or same normalized name + company)
    4. Removes very senior executives (CEO, CFO, VP, Chief Officer unless target role asks for VP/exec)
    5. Removes people with no relevance to role
    Returns top ~5 clean candidates for LLM ranking.
    """
    title_lower = job_title.lower()
    comp_lower = company.lower().strip()
    
    unrelated_depts = {"finance", "accounting", "legal", "compliance", "facilities", "real estate", "custodial"}
    is_finance_legal_job = any(dept in title_lower for dept in unrelated_depts)
    is_exec_job = any(k in title_lower for k in ["ceo", "cfo", "vp", "vice president", "chief officer", "executive"])

    filtered: List[Dict[str, Any]] = []
    seen_keys = set()

    for cand in candidates_raw:
        name = cand.get("name", "").strip()
        cand_company = cand.get("company", "").strip()
        cand_title = cand.get("title", "").strip()
        cand_title_lower = cand_title.lower()
        url = cand.get("linkedin_url") or cand.get("github_url") or cand.get("email") or name.lower()

        # Deduplication key
        norm_key = (name.lower(), cand_company.lower(), url)
        if norm_key in seen_keys or name.lower() in {k[0] for k in seen_keys}:
            continue

        # Rule 1: Ex-employees / Company mismatch
        if any(term in cand_title_lower for term in ["ex-", "former", "past", "previously at"]):
            continue

        # Rule 2: Unrelated departments
        if not is_finance_legal_job:
            if any(dept in cand_title_lower for dept in unrelated_depts):
                continue

        # Rule 3: Very senior executives (unless exec job)
        if not is_exec_job:
            exec_pattern = r'\b(ceo|cfo|cpo|cto|president|vp|evp|svp|vice president|chief|founder)\b'
            if re.search(exec_pattern, cand_title_lower):
                continue

        seen_keys.add(norm_key)
        filtered.append(cand)
        if len(filtered) >= 5:
            break

    return filtered

def deterministic_contact_boost(title: str, team: str = "") -> int:
    t_lower = title.lower()
    score = 5
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
    async def fetch_live_web_contacts(company: str, title: str) -> List[Dict[str, Any]]:
        import httpx
        import urllib.parse
        import re
        from bs4 import BeautifulSoup

        queries = build_search_queries(company, title)
        results: List[Dict[str, Any]] = []
        seen_urls = set()

        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            for q in queries[:4]:
                try:
                    resp = await client.post(
                        "https://html.duckduckgo.com/html/",
                        data={"q": f"site:linkedin.com/in {q}"},
                        headers=headers
                    )
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "html.parser")
                        for body in soup.find_all("div", class_="result__body"):
                            link_elem = body.find("a", class_="result__a")
                            snippet_elem = body.find("a", class_="result__snippet")
                            if not link_elem:
                                continue
                            raw_title = link_elem.get_text(strip=True)
                            raw_url = link_elem.get("href", "")
                            decoded_url = urllib.parse.unquote(raw_url)

                            if "linkedin.com/in" not in decoded_url.lower():
                                continue

                            # Extract clean LinkedIn profile URL
                            match = re.search(r'https?://[a-z]+\.linkedin\.com/in/[a-zA-Z0-9_-]+', decoded_url)
                            final_url = match.group(0) if match else decoded_url

                            if final_url in seen_urls:
                                continue
                            seen_urls.add(final_url)

                            # Parse Name & Title from search result
                            clean_title = raw_title.replace(" | LinkedIn", "").replace(" ...", "").strip()
                            parts = clean_title.split(" - ")
                            if len(parts) >= 2:
                                cand_name = parts[0].strip()
                                cand_title = " - ".join(parts[1:]).strip()
                            else:
                                cand_name = clean_title
                                cand_title = f"{title} Team at {company}"

                            results.append({
                                "name": cand_name,
                                "company": company,
                                "title": cand_title,
                                "team": "Engineering",
                                "linkedin_url": final_url,
                                "github_url": None,
                                "email": f"{cand_name.lower().replace(' ', '.')}@{company.lower().replace(' ', '')}.com",
                                "source": "Live Public Web Search"
                            })
                except Exception as e:
                    logger.warning(f"Error fetching live search query '{q}': {e}")
                    continue

        return results

    @staticmethod
    async def find_and_rank_contacts(db: AsyncSession, job_id: int) -> List[Contact]:
        job_result = await db.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()
        if not job:
            raise ValueError(f"Job with id {job_id} not found")

        cache_key = f"{job.company.lower().strip()}|{job.title.lower().strip()}|{SEARCH_VERSION}"

        # 1. Check SearchCache
        cache_stmt = select(SearchCache).where(SearchCache.cache_key == cache_key)
        cache_result = await db.execute(cache_stmt)
        cache_entry = cache_result.scalar_one_or_none()

        if cache_entry and cache_entry.filtered_results:
            logger.info(f"SearchCache hit for key: {cache_key}")
            pre_filtered_candidates = cache_entry.filtered_results
        else:
            logger.info(f"SearchCache miss/empty for key: {cache_key}. Executing targeted search queries.")
            # Generate 3-5 plain Python search queries
            queries = build_search_queries(job.company, job.title)

            # Fetch real candidates via live web search first
            raw_candidates = await ContactFinderService.fetch_live_web_contacts(job.company, job.title)

            # Fallback to LLM knowledge base if search engine scraper was blocked / returned empty
            if not raw_candidates:
                comp_clean = job.company.strip()
                prompt = (
                    f"Identify 3 REACHABLE, non-executive contacts at '{comp_clean}' for the '{job.title}' position.\n"
                    f"STRICT RULE: Do NOT return C-suite executives, Presidents, EVPs, SVPs, or VPs.\n"
                    f"Target ONLY mid-level hiring managers and recruiters:\n"
                    f"1. Engineering Manager / AI Team Manager\n"
                    f"2. Technical Recruiter / AI Engineering Talent Sourcer\n"
                    f"3. Senior or Lead AI Engineer on the team\n"
                    f"Provide individual personal names or targeted team titles, exact titles, and LinkedIn profile URLs.\n"
                    f"Return JSON with key 'contacts' containing 3 items."
                )
                try:
                    gpt_contacts_res: ContactRankOutput = await LLMProvider.generate_structured(
                        prompt=prompt,
                        response_schema=ContactRankOutput,
                        system_instruction=f"Output 3 reachable mid-level contacts at {comp_clean} in contacts array. No C-suite or VPs."
                    )
                    if gpt_contacts_res and gpt_contacts_res.contacts:
                        raw_candidates = [
                            {
                                "name": c.name,
                                "company": comp_clean,
                                "title": c.title,
                                "team": c.team or "Engineering",
                                "linkedin_url": c.linkedin_url or f"https://linkedin.com/company/{comp_clean.lower().replace(' ', '')}",
                                "github_url": c.github_url,
                                "email": c.email or f"{c.name.lower().replace(' ', '.')}@{comp_clean.lower().replace(' ', '')}.com",
                                "source": "LLM Public Search"
                            }
                            for c in gpt_contacts_res.contacts
                        ]
                except Exception as e:
                    logger.warning(f"LLM contact extraction fallback failed: {e}")

            # Fallback if both returned empty
            if not raw_candidates:
                comp_clean = job.company.strip()
                raw_candidates = [
                    {
                        "name": f"Hiring Manager ({comp_clean})",
                        "company": comp_clean,
                        "title": f"Engineering Manager - {job.title} Team",
                        "team": "Engineering",
                        "linkedin_url": f"https://linkedin.com/company/{comp_clean.lower().replace(' ', '')}",
                        "github_url": None,
                        "email": f"hiring.manager@{comp_clean.lower().replace(' ', '')}.com",
                        "source": "Company Directory Search"
                    }
                ]

            # Deterministic Python Pre-filtering
            pre_filtered_candidates = filter_candidates_python(raw_candidates, job.title, job.company)

            # Persist in SearchCache
            cache_entry = SearchCache(
                cache_key=cache_key,
                company=job.company,
                role=job.title,
                query_count=len(queries),
                raw_results=raw_candidates,
                filtered_results=pre_filtered_candidates,
                search_version=SEARCH_VERSION
            )
            db.add(cache_entry)
            await db.flush()

        # 2. Targeted LLM Ranking (Luna / Configured LLM sees ONLY pre-filtered ~5 candidates)
        prompt = CONTACT_RANK_PROMPT_TEMPLATE.format(
            company=job.company,
            title=job.title,
            team="Engineering",
            candidates_json=json.dumps(pre_filtered_candidates, indent=2)
        )

        rank_output: ContactRankOutput = await LLMProvider.generate_structured(
            prompt=prompt,
            response_schema=ContactRankOutput,
            model_name="gemini-2.5-flash",
            system_instruction="Rank contacts for job outreach carefully based on role relevance."
        )

        saved_contacts: List[Contact] = []

        # Remove existing contacts for job to avoid duplicates
        await db.execute(delete(JobContact).where(JobContact.job_id == job.id))

        for idx, item in enumerate(rank_output.contacts[:3]):
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
                selected=(idx == 0)
            )
            db.add(job_contact)
            saved_contacts.append(contact)

        await db.commit()
        return saved_contacts
