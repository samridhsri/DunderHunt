from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Job, Contact, CandidateProfile, OutreachEvent
from app.prompts.prompts import (
    OutreachDraftOutput,
    OUTREACH_DRAFT_PROMPT_TEMPLATE
)
from app.core.llm import LLMProvider

class OutreachService:
    @staticmethod
    async def generate_outreach_draft(
        db: AsyncSession,
        job_id: int,
        contact_id: int,
        channel: str = "LinkedIn",
        purpose: str = "Introduction"
    ) -> str:
        job = (await db.execute(select(Job).where(Job.id == job_id))).scalar_one_or_none()
        contact = (await db.execute(select(Contact).where(Contact.id == contact_id))).scalar_one_or_none()
        profile = (await db.execute(select(CandidateProfile).limit(1))).scalar_one_or_none()

        if not job or not contact:
            raise ValueError("Job or Contact record not found")

        candidate_name = profile.name if profile else "Sam"

        prompt = OUTREACH_DRAFT_PROMPT_TEMPLATE.format(
            contact_name=contact.name,
            contact_title=contact.title,
            company=job.company,
            job_title=job.title,
            candidate_name=candidate_name,
            channel=channel,
            purpose=purpose
        )

        result: OutreachDraftOutput = await LLMProvider.generate_structured(
            prompt=prompt,
            response_schema=OutreachDraftOutput,
            model_name="gemini-2.5-flash",
            system_instruction="Write a high-converting, concise outreach message for a tech job applicant."
        )

        # Log outreach event
        event = OutreachEvent(
            job_id=job.id,
            contact_id=contact.id,
            channel=channel,
            message=result.draft_message,
            response_status="Drafted"
        )
        db.add(event)
        await db.commit()

        return result.draft_message
