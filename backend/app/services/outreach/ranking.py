import re
import json
import logging
from typing import List, Dict, Any
from app.prompts.prompts import (
    ContactRankOutput,
    CONTACT_RANK_PROMPT_TEMPLATE
)
from app.core.llm import LLMProvider

logger = logging.getLogger(__name__)

def prefilter_and_score_python(candidates: List[Dict[str, Any]], job_title: str, company: str) -> List[Dict[str, Any]]:
    """
    Step 5: Python candidate pre-filtering & scoring before LLM evaluation.
    Rule 1: Eliminate company mismatch / ex-employees
    Rule 2: Eliminate unrelated departments & C-suite execs unless target role is executive
    Rule 3: Merge duplicates
    Rule 4: Apply scoring heuristics (Same company +40, Same team +30, Relevant role +20, Recruiter +15, Unrelated team -30, Exec -10)
    """
    title_lower = job_title.lower()
    comp_lower = company.strip().lower()

    unrelated_depts = {"finance", "accounting", "legal", "facilities", "custodial", "real estate"}
    is_finance_legal = any(dept in title_lower for dept in unrelated_depts)
    is_exec_job = any(k in title_lower for k in ["ceo", "cfo", "vp", "vice president", "chief", "executive"])

    filtered: List[Dict[str, Any]] = []
    seen_keys = set()

    for cand in candidates:
        name = cand.get("name", "").strip()
        cand_comp = cand.get("company", "").strip().lower()
        cand_title = cand.get("title", "").strip()
        cand_title_lower = cand_title.lower()
        url = cand.get("profile_url") or cand.get("linkedin_url") or cand.get("source_url") or name.lower()

        # Deduplication
        norm_key = (name.lower(), cand_comp, url)
        if norm_key in seen_keys or name.lower() in {k[0] for k in seen_keys}:
            continue

        # Rule 1: Ex-employees / Former
        if any(term in cand_title_lower for term in ["ex-", "former", "past", "previously at"]):
            continue

        # Rule 2: Unrelated depts
        if not is_finance_legal and any(dept in cand_title_lower for dept in unrelated_depts):
            continue

        # Rule 3: C-suite execs
        if not is_exec_job:
            exec_pattern = r'\b(ceo|cfo|cpo|cto|president|vp|evp|svp|vice president|chief|founder)\b'
            if re.search(exec_pattern, cand_title_lower):
                continue

        # Python Scoring Heuristic
        base_score = 0
        if cand_comp == comp_lower or comp_lower in cand_comp:
            base_score += 40
        if "engineering" in cand_title_lower or "ai" in cand_title_lower or "software" in cand_title_lower or "tech" in cand_title_lower:
            base_score += 30
        if any(k in cand_title_lower for k in ["manager", "lead", "director", "head"]):
            base_score += 20
        elif any(k in cand_title_lower for k in ["recruiter", "talent", "sourcer"]):
            base_score += 15
        
        cand_copy = dict(cand)
        cand_copy["heuristic_score"] = base_score
        seen_keys.add(norm_key)
        filtered.append(cand_copy)

    # Sort by Python score desc and take top 5
    filtered.sort(key=lambda x: x["heuristic_score"], reverse=True)
    return filtered[:5]

class CandidateRankingService:
    @staticmethod
    async def rank_candidates(job_title: str, company: str, prefiltered_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Step 6: Targeted LLM ranking of pre-filtered candidates.
        """
        if not prefiltered_candidates:
            return []

        prompt = CONTACT_RANK_PROMPT_TEMPLATE.format(
            company=company,
            title=job_title,
            team="Engineering",
            candidates_json=json.dumps(prefiltered_candidates, indent=2)
        )

        try:
            res: ContactRankOutput = await LLMProvider.generate_structured(
                prompt=prompt,
                response_schema=ContactRankOutput,
                model_name="gemini-2.5-flash",
                system_instruction="Rank candidate contacts strictly based on evidence provided in candidate snippets."
            )
            pref_map = {c["name"].lower(): c.get("profile_url") for c in prefiltered_candidates}
            ranked = []
            for item in res.contacts[:3]:
                url = item.linkedin_url or pref_map.get(item.name.lower())
                ranked.append({
                    "name": item.name,
                    "company": item.company or company,
                    "title": item.title,
                    "team": item.team or "Engineering",
                    "profile_url": url,
                    "email": item.email,
                    "overall_score": item.overall_score,
                    "recommendation_reason": item.recommendation_reason,
                    "source": item.source or "Serper Google API"
                })
            return ranked
        except Exception as e:
            logger.warning(f"Candidate LLM ranking failed: {e}")
            return [
                {
                    "name": c["name"],
                    "company": c["company"],
                    "title": c["title"],
                    "team": c.get("team", "Engineering"),
                    "profile_url": c.get("profile_url"),
                    "email": c.get("email"),
                    "overall_score": min(95, 60 + c.get("heuristic_score", 20)),
                    "recommendation_reason": f"Relevant role match at {company}",
                    "source": c.get("source", "Pre-filtered Search")
                }
                for c in prefiltered_candidates[:3]
            ]
