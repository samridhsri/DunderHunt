import logging
import json
from typing import List, Dict, Any
from app.prompts.prompts import (
    CandidateExtractionOutput,
    CANDIDATE_EXTRACTION_PROMPT_TEMPLATE
)
from app.core.llm import LLMProvider

logger = logging.getLogger(__name__)

class CandidateExtractionService:
    @staticmethod
    async def extract_candidates(company: str, role: str, raw_snippets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parses messy raw search snippets into structured candidate objects.
        Uses cheap LLM prompting focusing strictly on facts explicitly in snippets.
        """
        if not raw_snippets:
            return []

        prompt = CANDIDATE_EXTRACTION_PROMPT_TEMPLATE.format(
            company=company,
            role=role,
            snippets=json.dumps(raw_snippets, indent=2)
        )

        try:
            res: CandidateExtractionOutput = await LLMProvider.generate_structured(
                prompt=prompt,
                response_schema=CandidateExtractionOutput,
                model_name="gemini-2.5-flash",
                system_instruction="Extract explicit facts only without inferring employment or titles unsupported by snippets."
            )
            extracted = []
            for p in res.people:
                extracted.append({
                    "name": p.name,
                    "title": p.title,
                    "company": p.company or company,
                    "team": "Engineering",
                    "profile_url": p.profile_url,
                    "source_url": p.source_url,
                    "evidence": p.evidence or [f"Works as {p.title} at {p.company}"],
                    "source": "Extracted Search Snippet"
                })
            return extracted
        except Exception as e:
            logger.warning(f"Candidate extraction failed, using raw fallback: {e}")
            return raw_snippets
