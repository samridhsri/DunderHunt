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
from app.services.contact_finder import ContactFinderService
from app.services.outreach_service import OutreachService

api_router = APIRouter()

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
        # Sort priority A first, then fit score desc
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

    # Create or update application record
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

# --- FIND CONTACT API ---
@api_router.post("/jobs/{job_id}/find-contacts", response_model=FindContactsResponse)
async def find_contacts_for_job(job_id: int, db: AsyncSession = Depends(get_db)):
    try:
        contacts = await ContactFinderService.find_and_rank_contacts(db, job_id)
        contact_reads = [
            ContactRead(
                id=c.id,
                name=c.name,
                company=c.company,
                title=c.title,
                team=c.team,
                linkedin_url=c.linkedin_url,
                github_url=c.github_url,
                email=c.email,
                source=c.source,
                overall_score=c.overall_score,
                recommendation_reason=f"Top candidate match for {c.title}",
                selected=False
            )
            for c in contacts
        ]
        return FindContactsResponse(job_id=job_id, contacts=contact_reads)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- OUTREACH DRAFT API ---
@api_router.post("/jobs/{job_id}/outreach", response_model=OutreachDraftResponse)
async def generate_outreach_draft(job_id: int, req: OutreachDraftRequest, db: AsyncSession = Depends(get_db)):
    try:
        draft = await OutreachService.generate_outreach_draft(
            db, job_id=job_id, contact_id=req.contact_id, channel=req.channel, purpose=req.purpose
        )
        return OutreachDraftResponse(
            job_id=job_id,
            contact_id=req.contact_id,
            channel=req.channel,
            purpose=req.purpose,
            draft_message=draft
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

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
