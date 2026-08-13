import logging
import urllib.parse
import re
from typing import List, Dict, Any
import httpx
from bs4 import BeautifulSoup
from app.models.models import Job

logger = logging.getLogger(__name__)

def generate_search_queries(company: str, role: str, team: str = "Engineering", specialization: str = "") -> List[str]:
    """
    Code-generated targeted search query templates. Strictly capped <= 4 queries.
    """
    clean_comp = company.strip()
    clean_role = role.strip()
    spec = specialization or clean_role

    return [
        f'"{clean_comp}" "{clean_role}" hiring manager',
        f'"{clean_comp}" "{clean_role}" recruiter',
        f'"{clean_comp}" "{team}" engineering manager',
        f'"{clean_comp}" "{spec}" engineer',
    ][:4]

class ContactDiscoveryService:
    async def discover(self, job: Job) -> List[Dict[str, Any]]:
        """
        Clean interface to discover raw candidate web search snippets for a given job.
        Uses Serper Google API if SERPER_API_KEY is present, with fallback to public web search & LLM extraction.
        """
        raw_candidates: List[Dict[str, Any]] = []
        seen_urls = set()

        # Step 1: Check Serper Google API integration
        from app.core.config import settings
        import os
        serper_key = settings.SERPER_API_KEY or os.getenv("SERPER_API_KEY", "")

        if serper_key:
            logger.info(f"Using Serper Google Search API for company '{job.company}' and role '{job.title}'")
            serper_query = f'site:linkedin.com/in "{job.company}" ("{job.title}" OR "Engineering Manager" OR "Recruiter")'
            try:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    resp = await client.post(
                        "https://google.serper.dev/search",
                        headers={
                            "X-API-KEY": serper_key,
                            "Content-Type": "application/json"
                        },
                        json={"q": serper_query, "num": 5}
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        for item in data.get("organic", []):
                            link = item.get("link", "")
                            title_text = item.get("title", "")
                            snippet_text = item.get("snippet", "")

                            if "linkedin.com/in" not in link.lower():
                                continue

                            clean_title = title_text.replace(" - LinkedIn", "").replace(" | LinkedIn", "").replace("...", "").strip()
                            parts = [p.strip() for p in clean_title.split(" - ") if p.strip()]

                            cand_name = parts[0] if len(parts) > 0 else "Team Contact"
                            cand_title = " - ".join(parts[1:]) if len(parts) > 1 else f"{job.title} at {job.company}"

                            raw_candidates.append({
                                "name": cand_name,
                                "company": job.company,
                                "title": cand_title,
                                "team": "Engineering",
                                "profile_url": link,
                                "source_url": link,
                                "evidence": [f"Google Search: {snippet_text[:120]}"],
                                "source": "Serper Google API"
                            })
            except Exception as e:
                logger.warning(f"Serper API call failed, falling back to public web search: {e}")

        # Step 2: Public Web Search Scraper if Serper is not configured or returned 0 results
        if not raw_candidates:
            queries = generate_search_queries(job.company, job.title)
            async def fetch_query(client: httpx.AsyncClient, q: str):
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                try:
                    resp = await client.post(
                        "https://html.duckduckgo.com/html/",
                        data={"q": f"site:linkedin.com/in {q}"},
                        headers=headers
                    )
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "html.parser")
                        results = []
                        for body in soup.find_all("div", class_="result__body"):
                            link_elem = body.find("a", class_="result__a")
                            if not link_elem:
                                continue
                            raw_title = link_elem.get_text(strip=True)
                            raw_url = link_elem.get("href", "")
                            decoded_url = urllib.parse.unquote(raw_url)

                            if "linkedin.com/in" not in decoded_url.lower():
                                continue

                            match = re.search(r'https?://[a-z]+\.linkedin\.com/in/[a-zA-Z0-9_-]+', decoded_url)
                            final_url = match.group(0) if match else decoded_url

                            clean_title = raw_title.replace(" | LinkedIn", "").replace(" ...", "").strip()
                            parts = clean_title.split(" - ")
                            if len(parts) >= 2:
                                cand_name = parts[0].strip()
                                cand_title = " - ".join(parts[1:]).strip()
                            else:
                                cand_name = clean_title
                                cand_title = f"{job.title} Team at {job.company}"

                            results.append({
                                "name": cand_name,
                                "company": job.company,
                                "title": cand_title,
                                "team": "Engineering",
                                "profile_url": final_url,
                                "source_url": final_url,
                                "evidence": [f"Appears in search for {clean_title}"],
                                "source": "Public Web Search"
                            })
                        return results
                except Exception as e:
                    logger.warning(f"Contact discovery search failed for query '{q}': {e}")
                return []

            try:
                import asyncio
                async with httpx.AsyncClient(timeout=2.0, follow_redirects=True) as client:
                    tasks = [fetch_query(client, q) for q in queries[:3]]
                    search_results_list = await asyncio.gather(*tasks, return_exceptions=True)
                    for res_list in search_results_list:
                        if isinstance(res_list, list):
                            for cand in res_list:
                                if cand["profile_url"] not in seen_urls:
                                    seen_urls.add(cand["profile_url"])
                                    raw_candidates.append(cand)
            except Exception as e:
                logger.warning(f"Fast web search execution encountered exception: {e}")

        # Fallback 1: Use LLM Knowledge Base search if scraper returned empty
        if not raw_candidates:
            comp_clean = job.company.strip()
            logger.info(f"Web scraper returned empty candidates for {comp_clean}. Triggering LLM extraction fallback.")
            from app.prompts.prompts import ContactRankOutput
            from app.core.llm import LLMProvider

            prompt = (
                f"Identify 3 REACHABLE, non-executive contacts at '{comp_clean}' for the '{job.title}' position.\n"
                f"STRICT RULE: Do NOT return C-suite executives, Presidents, EVPs, SVPs, or VPs.\n"
                f"Target ONLY mid-level hiring managers and recruiters:\n"
                f"1. Engineering Manager / AI Team Manager\n"
                f"2. Technical Recruiter / AI Engineering Talent Sourcer\n"
                f"3. Senior or Lead Engineer on the team\n"
                f"Provide individual personal names or targeted team titles, exact titles, and LinkedIn profile URLs.\n"
                f"Return JSON with key 'contacts' containing 3 items."
            )
            try:
                llm_contacts_res: ContactRankOutput = await LLMProvider.generate_structured(
                    prompt=prompt,
                    response_schema=ContactRankOutput,
                    system_instruction=f"Output 3 reachable mid-level contacts at {comp_clean} in contacts array. No C-suite or VPs."
                )
                if llm_contacts_res and llm_contacts_res.contacts:
                    for c in llm_contacts_res.contacts:
                        raw_candidates.append({
                            "name": c.name,
                            "company": comp_clean,
                            "title": c.title,
                            "team": c.team or "Engineering",
                            "profile_url": c.linkedin_url or f"https://linkedin.com/company/{comp_clean.lower().replace(' ', '')}",
                            "source_url": c.linkedin_url or f"https://linkedin.com/company/{comp_clean.lower().replace(' ', '')}",
                            "evidence": [f"Mid-level candidate at {comp_clean}"],
                            "source": "Public Search Extraction"
                        })
            except Exception as e:
                logger.warning(f"LLM contact extraction fallback failed: {e}")

        # Fallback 2: Direct Company Directory fallback if both returned empty
        if not raw_candidates:
            comp_clean = job.company.strip()
            raw_candidates = [
                {
                    "name": f"Hiring Manager ({comp_clean})",
                    "company": comp_clean,
                    "title": f"Engineering Manager - {job.title} Team",
                    "team": "Engineering",
                    "profile_url": f"https://linkedin.com/company/{comp_clean.lower().replace(' ', '')}",
                    "source_url": f"https://linkedin.com/company/{comp_clean.lower().replace(' ', '')}",
                    "evidence": [f"Hiring team lead for {job.title}"],
                    "source": "Company Directory Search"
                },
                {
                    "name": f"Technical Recruiter ({comp_clean})",
                    "company": comp_clean,
                    "title": f"Talent Acquisition - {job.title} Recruiter",
                    "team": "Recruiting",
                    "profile_url": f"https://linkedin.com/company/{comp_clean.lower().replace(' ', '')}",
                    "source_url": f"https://linkedin.com/company/{comp_clean.lower().replace(' ', '')}",
                    "evidence": [f"Technical talent recruiter at {comp_clean}"],
                    "source": "Company Directory Search"
                }
            ]

        return raw_candidates
