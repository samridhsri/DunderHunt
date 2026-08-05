import re
import hashlib
from typing import Tuple, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Job
from app.schemas.schemas import JobIngestRequest

def normalize_string(val: Optional[str]) -> str:
    if not val:
        return ""
    # Lowercase, replace punctuation with hyphen, condense spaces
    val = val.lower().strip()
    val = re.sub(r'[^a-z0-9\s]', '', val)
    val = re.sub(r'\s+', '-', val)
    return val

def generate_canonical_fingerprint(company: str, title: str, location: Optional[str] = None) -> str:
    norm_company = normalize_string(company)
    norm_title = normalize_string(title)
    norm_location = normalize_string(location) or "remote"
    
    raw_str = f"{norm_company}|{norm_title}|{norm_location}"
    return hashlib.sha256(raw_str.encode('utf-8')).hexdigest()[:32]

class IngestionService:
    @staticmethod
    async def fetch_url_content(url: str) -> str:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Remove scripts, styles, metadata
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()
            text = soup.get_text(separator="\n")
            lines = (line.strip() for line in text.splitlines())
            clean_text = "\n".join(chunk for chunk in lines if chunk)
            return clean_text

    @staticmethod
    async def process_job_ingest(db: AsyncSession, request: JobIngestRequest) -> Tuple[Job, bool]:
        """
        Extracts, normalizes, fingerprints, checks duplicates, and saves job.
        Returns Tuple[Job, is_new_bool]
        """
        description = request.job_description or ""
        source_url = request.url
        company = request.company or "Unknown Company"
        title = request.title or "Software Engineer"
        location = request.location or "Remote"

        # If URL provided but no description, fetch URL content
        if source_url and not description:
            try:
                description = await IngestionService.fetch_url_content(source_url)
            except Exception as e:
                description = f"Content fetched from {source_url}. Error parsing html: {str(e)}"

        # Attempt to extract title/company from first lines of text if missing
        if description and (company == "Unknown Company" or title == "Software Engineer"):
            lines = [l.strip() for l in description.split("\n") if l.strip()]
            if lines and company == "Unknown Company":
                for l in lines[:5]:
                    if "at " in l.lower() or " - " in l:
                        parts = re.split(r' at | - ', l, flags=re.IGNORECASE)
                        if len(parts) >= 2:
                            title = parts[0].strip()
                            company = parts[1].strip()
                            break

        fingerprint = generate_canonical_fingerprint(company, title, location)

        # Check existing duplicate
        query = select(Job).where(Job.fingerprint == fingerprint)
        result = await db.execute(query)
        existing_job = result.scalar_one_or_none()

        if existing_job:
            return existing_job, False

        # Create new job record
        new_job = Job(
            company=company,
            title=title,
            location=location,
            remote_type="Remote" if "remote" in location.lower() else "Hybrid",
            employment_type="Full-time",
            description=description,
            requirements="Extracted requirements from job description",
            application_url=source_url or "https://example.com/apply",
            source_url=source_url,
            fingerprint=fingerprint,
            status="Discovered",
            next_action="Run Fit Analysis"
        )
        
        db.add(new_job)
        await db.commit()
        await db.refresh(new_job)
        return new_job, True
