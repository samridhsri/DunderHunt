import datetime
import logging
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.models.models import (
    Job, Contact, JobContact, OutreachStateRecord, OutreachEvent, SearchCache, CandidateProfile
)
from app.schemas.schemas import OutreachContext
from app.services.jobs.service import JobService
from app.services.contacts.service import ContactService
from app.services.outreach.discovery import ContactDiscoveryService
from app.services.outreach.extraction import CandidateExtractionService
from app.services.outreach.ranking import prefilter_and_score_python, CandidateRankingService
from app.services.outreach.verification import ContactVerificationService
from app.services.outreach.strategy import OutreachStrategyService
from app.services.outreach.messaging import MessageGeneratorService

logger = logging.getLogger(__name__)

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)

SEARCH_VERSION = "v8"

class OutreachService:
    @staticmethod
    async def get_or_create_state(db: AsyncSession, job_id: int) -> OutreachStateRecord:
        stmt = select(OutreachStateRecord).options(selectinload(OutreachStateRecord.selected_contact)).where(OutreachStateRecord.job_id == job_id)
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()
        if not record:
            record = OutreachStateRecord(job_id=job_id, state="OFF")
            db.add(record)
            await db.commit()
            await db.refresh(record)
        return record

    @staticmethod
    async def enable_outreach(db: AsyncSession, job_id: int) -> OutreachStateRecord:
        job = await JobService.get_job(db, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        state_rec = await OutreachService.get_or_create_state(db, job_id)
        new_state = "CHOOSING_CONTACT" if not state_rec.selected_contact_id else "CONTACT_SELECTED"
        state_rec.state = new_state
        await JobService.update_outreach_status(db, job_id, True, new_state)
        await db.commit()
        await db.refresh(state_rec)
        return state_rec

    @staticmethod
    async def disable_outreach(db: AsyncSession, job_id: int) -> OutreachStateRecord:
        job = await JobService.get_job(db, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        state_rec = await OutreachService.get_or_create_state(db, job_id)
        state_rec.state = "OFF"
        await JobService.update_outreach_status(db, job_id, False, "OFF")
        await db.commit()
        await db.refresh(state_rec)
        return state_rec

    @staticmethod
    async def discover_contacts_for_job(db: AsyncSession, job_id: int) -> List[Contact]:
        job = await JobService.get_job(db, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Item 17: Cache Key format: contact_discovery:{company}:{team}:{role}
        cache_key = f"contact_discovery:{job.company.lower().strip()}:engineering:{job.title.lower().strip()}"

        # 1. Check SearchCache
        cache_stmt = select(SearchCache).where(SearchCache.cache_key == cache_key)
        cache_res = await db.execute(cache_stmt)
        cache_entry = cache_res.scalar_one_or_none()

        if cache_entry and cache_entry.filtered_results:
            logger.info(f"SearchCache hit for key: {cache_key}")
            verified_candidates = cache_entry.filtered_results
        else:
            logger.info(f"SearchCache miss/empty for key: {cache_key}. Executing discovery service.")
            discovery_service = ContactDiscoveryService()
            raw_candidates = await discovery_service.discover(job)

            # Extract structured candidates
            extracted = await CandidateExtractionService.extract_candidates(job.company, job.title, raw_candidates)

            # Python Pre-filtering
            prefiltered = prefilter_and_score_python(extracted, job.title, job.company)

            # LLM Ranking
            ranked = await CandidateRankingService.rank_candidates(job.title, job.company, prefiltered)

            # Step 7: Verification
            verified_candidates = []
            for item in ranked:
                verified = ContactVerificationService.verify_candidate(item, job.company, job.title)
                if verified:
                    verified_candidates.append(verified)

            if not verified_candidates and ranked:
                verified_candidates = ranked

            # Save or update SearchCache
            if not cache_entry:
                cache_entry = SearchCache(
                    cache_key=cache_key,
                    company=job.company,
                    role=job.title,
                    query_count=4,
                    raw_results=raw_candidates,
                    filtered_results=verified_candidates,
                    search_version=SEARCH_VERSION
                )
                db.add(cache_entry)
            else:
                cache_entry.raw_results = raw_candidates
                cache_entry.filtered_results = verified_candidates
                cache_entry.search_version = SEARCH_VERSION
            await db.flush()

        # Update DB JobContact records
        await db.execute(delete(JobContact).where(JobContact.job_id == job.id))

        saved_contacts: List[Contact] = []
        for idx, item in enumerate(verified_candidates[:3]):
            contact = Contact(
                name=item["name"],
                company=item["company"],
                title=item["title"],
                team=item.get("team", "Engineering"),
                relationship="Public contact",
                linkedin_url=item.get("profile_url") or item.get("linkedin_url"),
                email=item.get("email"),
                source=item.get("source", "Public Web Search"),
                overall_score=item.get("overall_score", 85),
                company_verified=item.get("company_verified", True),
                role_verified=item.get("role_verified", True),
                verification_confidence=item.get("verification_confidence", 0.9),
                last_verified_at=utcnow()
            )
            db.add(contact)
            await db.flush()

            job_contact = JobContact(
                job_id=job.id,
                contact_id=contact.id,
                recommended=True,
                recommendation_reason=item.get("recommendation_reason", f"Relevant contact at {job.company}"),
                selected=(idx == 0)
            )
            db.add(job_contact)
            saved_contacts.append(contact)

        # Update Outreach State
        state_rec = await OutreachService.get_or_create_state(db, job_id)
        if saved_contacts and not state_rec.selected_contact_id:
            state_rec.selected_contact_id = saved_contacts[0].id
            state_rec.state = "CONTACT_SELECTED"

        await db.commit()
        return saved_contacts

    @staticmethod
    async def select_contact_for_job(db: AsyncSession, job_id: int, contact_id: int) -> OutreachStateRecord:
        contact = await ContactService.get_by_id(db, contact_id)
        if not contact:
            raise ValueError(f"Contact {contact_id} not found")

        state_rec = await OutreachService.get_or_create_state(db, job_id)
        state_rec.selected_contact_id = contact.id
        state_rec.state = "CONTACT_SELECTED"

        # Update JobContact selection flags
        res = await db.execute(select(JobContact).where(JobContact.job_id == job_id))
        job_contacts = res.scalars().all()
        for jc in job_contacts:
            jc.selected = (jc.contact_id == contact_id)

        await db.commit()
        await db.refresh(state_rec)
        return state_rec

    @staticmethod
    async def generate_draft_message(
        db: AsyncSession,
        job_id: int,
        contact_id: Optional[int] = None,
        channel: str = "LinkedIn",
        purpose: str = "Introduce myself"
    ) -> OutreachStateRecord:
        job = await JobService.get_job(db, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        state_rec = await OutreachService.get_or_create_state(db, job_id)
        cid = contact_id or state_rec.selected_contact_id
        if not cid:
            raise ValueError("No contact selected for outreach")

        contact = await ContactService.get_by_id(db, cid)
        if not contact:
            raise ValueError(f"Contact {cid} not found")

        # Validate channel & purpose
        valid_chan, valid_purp = OutreachStrategyService.validate_strategy(channel, purpose)
        state_rec.channel = valid_chan
        state_rec.purpose = valid_purp

        # Load profile context
        prof_res = await db.execute(select(CandidateProfile).limit(1))
        profile = prof_res.scalar_one_or_none()
        cand_name = profile.name if profile else "Sam"
        exp_summary = "AI Engineer with experience in agentic workflows, RAG, and FastAPI service architecture."

        outreach_ctx = OutreachContext(
            job_title=job.title,
            company=job.company,
            contact_name=contact.name,
            contact_title=contact.title,
            relationship=contact.relationship or "Professional",
            relevant_user_experience=exp_summary,
            purpose=valid_purp,
            channel=valid_chan
        )

        state_rec.state = "DRAFTING"
        await db.flush()

        draft_output = await MessageGeneratorService.generate_draft(outreach_ctx, candidate_name=cand_name)
        state_rec.current_draft = draft_output.draft_message
        state_rec.draft_subject = draft_output.subject
        state_rec.draft_reasoning = draft_output.reasoning
        state_rec.selected_contact_id = contact.id
        state_rec.state = "DRAFT_READY"

        await db.commit()
        await db.refresh(state_rec)
        return state_rec

    @staticmethod
    async def update_draft(db: AsyncSession, job_id: int, draft_message: str, subject: Optional[str] = None) -> OutreachStateRecord:
        state_rec = await OutreachService.get_or_create_state(db, job_id)
        state_rec.current_draft = draft_message
        if subject is not None:
            state_rec.draft_subject = subject
        state_rec.state = "DRAFT_READY"
        await db.commit()
        await db.refresh(state_rec)
        return state_rec

    @staticmethod
    async def mark_sent(db: AsyncSession, job_id: int, channel: Optional[str] = None) -> OutreachEvent:
        state_rec = await OutreachService.get_or_create_state(db, job_id)
        if not state_rec.selected_contact_id or not state_rec.current_draft:
            raise ValueError("Cannot mark sent without selected contact and draft message")

        ch = channel or state_rec.channel

        event = OutreachEvent(
            job_id=job_id,
            contact_id=state_rec.selected_contact_id,
            channel=ch,
            subject=state_rec.draft_subject,
            message=state_rec.current_draft,
            sent_at=utcnow(),
            status="sent",
            is_follow_up=False,
            sequence_number=1
        )
        db.add(event)
        state_rec.state = "SENT"
        await JobService.update_outreach_status(db, job_id, True, "SENT")
        await db.commit()
        await db.refresh(event)
        return event

    @staticmethod
    async def generate_followup_draft(db: AsyncSession, job_id: int, notes: Optional[str] = None) -> OutreachStateRecord:
        job = await JobService.get_job(db, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        state_rec = await OutreachService.get_or_create_state(db, job_id)

        # Get last sent event
        event_res = await db.execute(
            select(OutreachEvent)
            .where(OutreachEvent.job_id == job_id)
            .order_by(OutreachEvent.sent_at.desc())
            .limit(1)
        )
        last_event = event_res.scalar_one_or_none()

        if not last_event or not state_rec.selected_contact:
            raise ValueError("No prior sent outreach event found for follow-up")

        sent_str = last_event.sent_at.strftime("%b %d, %Y")
        contact = state_rec.selected_contact

        followup_out = await MessageGeneratorService.generate_followup(
            contact_name=contact.name,
            contact_title=contact.title,
            company=job.company,
            channel=last_event.channel,
            previous_message=last_event.message,
            sent_at=sent_str,
            notes=notes
        )

        state_rec.current_draft = followup_out.follow_up_message
        state_rec.draft_reasoning = followup_out.reasoning
        state_rec.state = "FOLLOW_UP_AVAILABLE"

        await db.commit()
        await db.refresh(state_rec)
        return state_rec

    @staticmethod
    async def get_outreach_events(db: AsyncSession, job_id: int) -> List[OutreachEvent]:
        res = await db.execute(
            select(OutreachEvent)
            .where(OutreachEvent.job_id == job_id)
            .order_by(OutreachEvent.sent_at.desc())
        )
        return list(res.scalars().all())
