import json
import logging
from typing import Dict, Any, Type, TypeVar
import httpx
from pydantic import BaseModel
from app.core.config import settings

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

class LLMProvider:
    @staticmethod
    async def generate_structured(
        prompt: str,
        response_schema: Type[T],
        model_name: str = "gemini-2.5-flash",
        system_instruction: str = "You are a precise JSON evaluation assistant."
    ) -> T:
        provider = settings.LLM_PROVIDER.lower()
        
        # Fallback to Mock if API keys are missing or provider set to mock
        if provider == "mock" or (provider == "gemini" and not settings.GEMINI_API_KEY) or (provider == "openai" and not settings.OPENAI_API_KEY):
            logger.info("Using Mock LLM Provider")
            return LLMProvider._generate_mock(prompt, response_schema)
        
        if provider == "gemini":
            return await LLMProvider._call_gemini(prompt, response_schema, settings.GEMINI_API_KEY, system_instruction)
        elif provider == "openai":
            return await LLMProvider._call_openai(prompt, response_schema, settings.OPENAI_API_KEY, system_instruction)
        else:
            return LLMProvider._generate_mock(prompt, response_schema)

    @staticmethod
    def _generate_mock(prompt: str, response_schema: Type[T]) -> T:
        schema_name = response_schema.__name__
        
        if "JobFitOutput" in schema_name:
            mock_data = {
                "technical_fit": 92,
                "experience_fit": 88,
                "education_fit": 95,
                "location_fit": 90,
                "authorization_fit": 100,
                "career_alignment": 90,
                "overall_score": 91,
                "priority": "A",
                "recommendation": "APPLY",
                "strengths": [
                    "Strong background in Python and Machine Learning/AI",
                    "Graduate degree aligns with candidate profile",
                    "Direct project experience in AI/ML stack"
                ],
                "concerns": [
                    "Limited explicit large-scale production SWE experience"
                ],
                "skill_gaps": [
                    "Docker containerization in high-load production"
                ],
                "resume_changes_needed": [
                    "Highlight bullet #2 regarding model optimization",
                    "Add Docker to skills list"
                ],
                "reasoning_summary": "Candidate profile matches technical requirements strongly with minor gaps in MLOps."
            }
            return response_schema(**mock_data)
        
        elif "ContactRankOutput" in schema_name:
            mock_data = {
                "contacts": [
                    {
                        "name": "Sarah Chen",
                        "company": "Target Company",
                        "title": "Engineering Manager - AI Platform",
                        "team": "AI Platform",
                        "linkedin_url": "https://linkedin.com/in/sarahchen-ai",
                        "github_url": None,
                        "email": "sarah.chen@example.com",
                        "source": "Company Org Page",
                        "overall_score": 94,
                        "recommendation_reason": "Manages the relevant engineering organization.",
                        "selected": False
                    },
                    {
                        "name": "John Smith",
                        "company": "Target Company",
                        "title": "Senior ML Engineer",
                        "team": "AI Platform",
                        "linkedin_url": "https://linkedin.com/in/johnsmith-ml",
                        "github_url": "https://github.com/johnsmith-ml",
                        "email": "john.smith@example.com",
                        "source": "GitHub",
                        "overall_score": 88,
                        "recommendation_reason": "Works in the exact technical area.",
                        "selected": False
                    },
                    {
                        "name": "Mike Davis",
                        "company": "Target Company",
                        "title": "Technical Recruiter - Engineering",
                        "team": "Talent Acquisition",
                        "linkedin_url": "https://linkedin.com/in/mikedavis-recruiter",
                        "github_url": None,
                        "email": "mike.davis@example.com",
                        "source": "Public Web Search",
                        "overall_score": 79,
                        "recommendation_reason": "Technical recruiter for engineering roles.",
                        "selected": False
                    }
                ]
            }
            return response_schema(**mock_data)
            
        elif "OutreachDraftOutput" in schema_name:
            mock_data = {
                "draft_message": "Hi, I noticed your team's recent work on AI Platform systems. Given my background in Machine Learning and backend engineering, I'd love to learn more about the team's upcoming roadmap and share how my experience aligns with the role."
            }
            return response_schema(**mock_data)

        # Fallback default
        return response_schema.model_construct()

    @staticmethod
    async def _call_gemini(prompt: str, response_schema: Type[T], api_key: str, system_instruction: str) -> T:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": f"{system_instruction}\n\n{prompt}"}]}],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, json=payload)
            res.raise_for_status()
            data = res.json()
            text_content = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed_json = json.loads(text_content)
            return response_schema(**parsed_json)

    @staticmethod
    async def _call_openai(prompt: str, response_schema: Type[T], api_key: str, system_instruction: str) -> T:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            text_content = data["choices"][0]["message"]["content"]
            parsed_json = json.loads(text_content)
            return response_schema(**parsed_json)
