from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.models import Startup, StartupContact
from app.schemas.schemas import (
    StartupEnrichRequest,
    StartupEnrichmentResponse,
    StartupCreate,
    StartupRead,
    StartupContactRead,
    StartupDraftPitchRequest,
    StartupDraftPitchResponse
)
from app.services.startup_service import StartupService

router = APIRouter()

@router.post("/enrich", response_model=StartupEnrichmentResponse)
async def enrich_startup(
    payload: StartupEnrichRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Automated company enrichment: Auto-detects company size, funding stage, tech stack, and summary.
    """
    if not payload.domain_or_name or not payload.domain_or_name.strip():
        raise HTTPException(status_code=400, detail="Domain or startup name is required.")
    
    return await StartupService.enrich_startup(db, payload.domain_or_name)

@router.post("/", response_model=StartupRead, status_code=status.HTTP_201_CREATED)
async def create_startup(
    payload: StartupCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Save a new startup record into DunderHunt.
    """
    clean_domain = payload.domain.strip().lower() if payload.domain else None
    if clean_domain:
        res = await db.execute(select(Startup).where(Startup.domain == clean_domain))
        existing = res.scalar_one_or_none()
        if existing:
            return existing

    startup = Startup(
        name=payload.name,
        domain=clean_domain,
        company_size=payload.company_size,
        funding_stage=payload.funding_stage,
        summary=payload.summary,
        tech_stack=payload.tech_stack,
        target_roles=payload.target_roles,
        website_url=payload.website_url,
        notes=payload.notes
    )
    db.add(startup)
    await db.commit()
    await db.refresh(startup)
    return startup

@router.get("/", response_model=List[StartupRead])
async def list_startups(
    db: AsyncSession = Depends(get_db)
):
    """
    List all tracked startups with their contacts.
    """
    res = await db.execute(select(Startup).options(selectinload(Startup.contacts)).order_by(Startup.created_at.desc()))
    return list(res.scalars().all())

@router.get("/{startup_id}", response_model=StartupRead)
async def get_startup(
    startup_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get details for a single startup.
    """
    res = await db.execute(select(Startup).options(selectinload(Startup.contacts)).where(Startup.id == startup_id))
    startup = res.scalar_one_or_none()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    return startup

@router.post("/{startup_id}/contacts/discover", response_model=List[StartupContactRead])
async def discover_startup_contacts(
    startup_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Discover key named contacts for a startup based on company size persona routing.
    """
    res = await db.execute(select(Startup).where(Startup.id == startup_id))
    startup = res.scalar_one_or_none()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")

    return await StartupService.discover_startup_contacts(db, startup)

@router.post("/contacts/{contact_id}/draft", response_model=StartupDraftPitchResponse)
async def draft_startup_pitch(
    contact_id: int,
    payload: StartupDraftPitchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a candidate-matched personalized cold outreach pitch for a startup contact.
    """
    res = await db.execute(select(StartupContact).where(StartupContact.id == contact_id))
    contact = res.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Startup contact not found")

    return await StartupService.generate_pitch(
        db=db,
        contact=contact,
        channel=payload.channel,
        purpose=payload.purpose
    )

@router.delete("/{startup_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_startup(
    startup_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a startup record and its contacts.
    """
    res = await db.execute(select(Startup).where(Startup.id == startup_id))
    startup = res.scalar_one_or_none()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")

    await db.delete(startup)
    await db.commit()
    return None
