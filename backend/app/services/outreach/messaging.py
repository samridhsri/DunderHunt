import logging
from typing import Optional
from app.schemas.schemas import OutreachContext
from app.prompts.prompts import (
    OutreachDraftOutput,
    FollowUpDraftOutput,
    OUTREACH_DRAFT_PROMPT_TEMPLATE,
    FOLLOW_UP_DRAFT_PROMPT_TEMPLATE
)
from app.core.llm import LLMProvider

logger = logging.getLogger(__name__)

class MessageGeneratorService:
    @staticmethod
    async def generate_draft(ctx: OutreachContext, candidate_name: str = "Sam") -> OutreachDraftOutput:
        """
        Step 11 & 12: Generates a single, personalized outreach draft from OutreachContext.
        """
        prompt = OUTREACH_DRAFT_PROMPT_TEMPLATE.format(
            contact_name=ctx.contact_name,
            contact_title=ctx.contact_title,
            company=ctx.company,
            relationship=ctx.relationship or "Professional",
            contact_context=f"Targeting {ctx.contact_name} ({ctx.contact_title}) at {ctx.company}",
            job_title=ctx.job_title,
            job_url="N/A",
            company_context=f"Company: {ctx.company}",
            purpose=ctx.purpose,
            candidate_name=candidate_name,
            relevant_user_experience=ctx.relevant_user_experience or "AI/ML software engineering and system architecture",
            relevant_user_projects="N/A",
            candidate_differentiators="N/A",
            channel=ctx.channel
        )

        try:
            res: OutreachDraftOutput = await LLMProvider.generate_structured(
                prompt=prompt,
                response_schema=OutreachDraftOutput,
                model_name="gemini-2.5-flash",
                system_instruction="Write a high-converting, concise outreach message for a job applicant."
            )
            return res
        except Exception as e:
            logger.warning(f"Draft generation failed, using fallback draft: {e}")
            fallback_subject = f"Connecting re: {ctx.job_title} role at {ctx.company}" if ctx.channel == "Email" else None
            fallback_text = (
                f"Hi {ctx.contact_name},\n\n"
                f"I noticed your work as {ctx.contact_title} at {ctx.company}. "
                f"I'm applying for the {ctx.job_title} position and would love to learn more about the team's technical roadmap.\n\n"
                f"Best,\n{candidate_name}"
            )
            return OutreachDraftOutput(
                draft_message=fallback_text,
                subject=fallback_subject,
                reasoning="Fallback template used due to temporary LLM generation error."
            )

    @staticmethod
    async def generate_followup(
        contact_name: str,
        contact_title: str,
        company: str,
        channel: str,
        previous_message: str,
        sent_at: str,
        notes: Optional[str] = None
    ) -> FollowUpDraftOutput:
        """
        Step 15: Context-aware follow-up draft generation.
        """
        prompt = FOLLOW_UP_DRAFT_PROMPT_TEMPLATE.format(
            contact_name=contact_name,
            contact_title=contact_title,
            company=company,
            channel=channel,
            sent_at=sent_at,
            previous_message=previous_message,
            notes=notes or "Polite follow-up check-in."
        )

        try:
            res: FollowUpDraftOutput = await LLMProvider.generate_structured(
                prompt=prompt,
                response_schema=FollowUpDraftOutput,
                model_name="gemini-2.5-flash",
                system_instruction="Write a short, professional follow-up message."
            )
            return res
        except Exception as e:
            logger.warning(f"Follow-up draft generation failed, using fallback: {e}")
            fallback_text = (
                f"Hi {contact_name},\n\n"
                f"Following up on my previous message regarding the team at {company}. "
                f"I'd still welcome a brief chat if your schedule permits!\n\n"
                f"Best,\nSam"
            )
            return FollowUpDraftOutput(
                follow_up_message=fallback_text,
                reasoning="Fallback follow-up template."
            )
