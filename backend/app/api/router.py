from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.core.database import get_db, init_db
from app.models.models import CandidateProfile, Job, JobAnalysis, Contact, JobContact, Application
from app.schemas.schemas import (
    CandidateProfileRead, CandidateProfileUpdate,
    JobIngestRequest, JobRead, JobAnalysisRead, DecisionUpdateRequest,
    ContactRead, FindContactsResponse, OutreachDraftRequest, OutreachDraftResponse,
    ApplicationRead, ApplicationUpdate
)
from app.services.ingestion import IngestionService
from app.services.fit_engine import FitEngineService
from app.services.outreach.service import OutreachService
from app.services.contacts.service import ContactService
from app.schemas.schemas import (
    CandidateProfileRead, CandidateProfileUpdate,
    JobIngestRequest, JobRead, JobAnalysisRead, DecisionUpdateRequest,
    ContactRead, ContactImportRequest, ContactSelectRequest, FindContactsResponse,
    OutreachToggleRequest, OutreachStateRead, OutreachDraftRequest, OutreachDraftUpdateRequest,
    OutreachDraftResponse, OutreachMarkSentRequest, OutreachFollowUpRequest, OutreachEventRead,
    ApplicationRead, ApplicationUpdate
)

from app.api.v1.endpoints.startups import router as startups_router

api_router = APIRouter()
api_router.include_router(startups_router, prefix="/startups", tags=["startups"])


# --- PROFILE API ---
@api_router.get("/profile", response_model=CandidateProfileRead)
async def get_profile(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CandidateProfile).limit(1))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = CandidateProfile(
            name="Sam",
            email="sam@example.com",
            skills={"Python": 9, "Machine Learning": 8, "Deep Learning": 8, "Agentic AI": 9, "FastAPI": 8, "TypeScript / Next.js": 8, "PyTorch": 7, "SQL": 8},
            target_roles=["AI Engineer", "ML Engineer", "Software Engineer", "Full Stack AI Developer"],
            target_locations=["New York, NY", "Remote"],
            work_authorization={"status": "US Citizen / Authorized"},
            experience=[
                {
                    "id": "exp_1",
                    "company": "AI Systems & Solutions",
                    "role": "AI / ML Engineer",
                    "location": "New York, NY",
                    "start_date": "2024-01",
                    "end_date": "Present",
                    "current": True,
                    "description": "Architected agentic AI workflows, RAG pipelines, and API integrations for automated decision support systems.",
                    "technologies": ["Python", "FastAPI", "OpenAI / Gemini APIs", "LangChain", "Vector Databases"]
                },
                {
                    "id": "exp_2",
                    "company": "Tech Ventures",
                    "role": "Software Engineering Intern",
                    "location": "Remote",
                    "start_date": "2023-05",
                    "end_date": "2023-12",
                    "current": False,
                    "description": "Built scalable REST services and dashboard frontends. Reduced API latency by 35% using caching and query optimization.",
                    "technologies": ["Python", "PostgreSQL", "React", "Docker"]
                }
            ],
            projects=[
                {
                    "id": "proj_1",
                    "title": "DunderHunt Decision Support Engine",
                    "role": "Lead Architect",
                    "url": "https://github.com/sam/dunderhunt",
                    "description": "Full-stack decision support platform that ingests job postings, performs 2-layer fit evaluation (deterministic + LLM), and manages outreach pipelines.",
                    "technologies": ["Next.js", "FastAPI", "SQLAlchemy", "Pydantic v2", "Gemini 2.5"],
                    "highlights": ["Zero-hallucination deterministic filter layer", "Sub-second fit scoring pipeline"]
                },
                {
                    "id": "proj_2",
                    "title": "Multi-Agent Workflow Orchestrator",
                    "role": "Creator",
                    "url": "https://github.com/sam/agent-orchestrator",
                    "description": "Autonomous multi-agent task execution framework with function calling and tool execution verification.",
                    "technologies": ["Python", "AsyncIO", "Pydantic", "LLM Structured Outputs"],
                    "highlights": ["Handled complex multi-turn API tool calls", "Integrated structured schema validation"]
                }
            ],
            resume_versions={"Resume v1": "General Software Engineer", "Resume v2": "ML Engineer", "Resume v3": "AI Systems Engineer"}
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile

@api_router.put("/profile", response_model=CandidateProfileRead)
async def update_profile(data: CandidateProfileUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CandidateProfile).limit(1))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = CandidateProfile()
        db.add(profile)

    for key, val in data.model_dump().items():
        setattr(profile, key, val)

    await db.commit()
    await db.refresh(profile)
    return profile

# --- JOB INGESTION & QUEUE API ---
@api_router.post("/jobs/ingest", response_model=JobRead)
async def ingest_job(request: JobIngestRequest, db: AsyncSession = Depends(get_db)):
    if not request.url and not request.job_description and not (request.title and request.company):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide at least job URL, job description, or Title + Company"
        )
    job, is_new = await IngestionService.process_job_ingest(db, request)
    
    # Auto-run Layer 1 & 2 Fit evaluation on ingestion
    await FitEngineService.evaluate_job_fit(db, job.id)
    
    # Reload job with analysis
    res = await db.execute(select(Job).where(Job.id == job.id))
    job = res.scalar_one()
    return job

@api_router.get("/jobs", response_model=List[JobRead])
async def list_jobs(
    priority: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Job).options(selectinload(Job.analysis))
    if priority:
        query = query.where(Job.priority == priority)
    if status_filter:
        query = query.where(Job.status == status_filter)

    query = query.order_by(
        Job.priority.asc(),
        desc(Job.fit_score)
    )
    result = await db.execute(query)
    return result.scalars().all()

@api_router.get("/jobs/{job_id}", response_model=JobRead)
async def get_job_detail(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).options(selectinload(Job.analysis)).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@api_router.post("/jobs/{job_id}/analyze", response_model=JobAnalysisRead)
async def run_job_analysis(job_id: int, db: AsyncSession = Depends(get_db)):
    try:
        analysis = await FitEngineService.evaluate_job_fit(db, job_id)
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@api_router.post("/jobs/{job_id}/decision", response_model=JobRead)
async def update_job_decision(job_id: int, request: DecisionUpdateRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    decision = request.decision.upper()
    if decision == "APPLY":
        job.recommendation = "APPLY"
        job.status = "Applied"
        job.next_action = "Outreach or Wait for response"
    elif decision == "SAVE":
        job.recommendation = "SAVE"
        job.status = "Saved"
        job.next_action = "Review later"
    elif decision == "SKIP":
        job.recommendation = "SKIP"
        job.status = "Withdrawn"
        job.next_action = "Skipped"

    app_res = await db.execute(select(Application).where(Application.job_id == job.id))
    app_rec = app_res.scalar_one_or_none()
    if not app_rec:
        app_rec = Application(job_id=job.id, status=job.status, notes=request.notes)
        db.add(app_rec)
    else:
        app_rec.status = job.status
        if request.notes:
            app_rec.notes = request.notes

    await db.commit()
    await db.refresh(job)
    return job

# --- OUTREACH MODULE API ---
@api_router.post("/jobs/{job_id}/outreach/enable", response_model=OutreachStateRead)
async def enable_outreach(job_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await OutreachService.enable_outreach(db, job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@api_router.post("/jobs/{job_id}/outreach/disable", response_model=OutreachStateRead)
async def disable_outreach(job_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await OutreachService.disable_outreach(db, job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@api_router.get("/jobs/{job_id}/outreach", response_model=OutreachStateRead)
async def get_outreach_state(job_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await OutreachService.get_or_create_state(db, job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@api_router.get("/jobs/{job_id}/contacts", response_model=List[ContactRead])
async def get_job_contacts(job_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(Contact)
        .join(JobContact, JobContact.contact_id == Contact.id)
        .where(JobContact.job_id == job_id)
    )
    return list(res.scalars().all())

@api_router.post("/jobs/{job_id}/contacts/discover", response_model=List[ContactRead])
async def discover_contacts(job_id: int, db: AsyncSession = Depends(get_db)):
    try:
        contacts = await OutreachService.discover_contacts_for_job(db, job_id)
        return contacts
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@api_router.post("/jobs/{job_id}/contacts/select", response_model=OutreachStateRead)
async def select_contact(job_id: int, req: ContactSelectRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await OutreachService.select_contact_for_job(db, job_id, req.contact_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@api_router.post("/contacts/import", response_model=ContactRead)
async def import_contact(req: ContactImportRequest, db: AsyncSession = Depends(get_db)):
    return await ContactService.import_contact(db, req)

@api_router.get("/contacts", response_model=List[ContactRead])
async def search_contacts(
    company: Optional[str] = None,
    query: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    return await ContactService.get_contacts(db, company=company, query=query)

@api_router.post("/jobs/{job_id}/outreach/draft", response_model=OutreachStateRead)
async def generate_draft(job_id: int, req: OutreachDraftRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await OutreachService.generate_draft_message(
            db, job_id, contact_id=req.contact_id, channel=req.channel, purpose=req.purpose
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@api_router.put("/jobs/{job_id}/outreach/draft", response_model=OutreachStateRead)
async def update_draft(job_id: int, req: OutreachDraftUpdateRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await OutreachService.update_draft(db, job_id, req.draft_message, req.subject)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@api_router.post("/jobs/{job_id}/outreach/sent", response_model=OutreachEventRead)
async def mark_sent(job_id: int, req: OutreachMarkSentRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await OutreachService.mark_sent(db, job_id, channel=req.channel)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.post("/jobs/{job_id}/outreach/follow-up", response_model=OutreachStateRead)
async def generate_followup(job_id: int, req: OutreachFollowUpRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await OutreachService.generate_followup_draft(db, job_id, notes=req.notes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/jobs/{job_id}/outreach/events", response_model=List[OutreachEventRead])
async def list_outreach_events(job_id: int, db: AsyncSession = Depends(get_db)):
    return await OutreachService.get_outreach_events(db, job_id)

# --- APPLICATION TRACKING API ---
@api_router.put("/applications/{job_id}", response_model=ApplicationRead)
async def update_application(job_id: int, req: ApplicationUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Application).where(Application.job_id == job_id))
    app_rec = res.scalar_one_or_none()
    if not app_rec:
        app_rec = Application(job_id=job_id)
        db.add(app_rec)

    for key, val in req.model_dump(exclude_unset=True).items():
        setattr(app_rec, key, val)

    await db.commit()
    await db.refresh(app_rec)
    return app_rec

