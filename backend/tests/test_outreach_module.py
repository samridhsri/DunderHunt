import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base
from app.models.models import Job, Contact
from app.schemas.schemas import JobIngestRequest, ContactImportRequest
from app.services.ingestion import IngestionService
from app.services.contacts.service import ContactService
from app.services.outreach.service import OutreachService

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_outreach_toggle(async_db: AsyncSession):
    req = JobIngestRequest(company="Notion", title="AI Engineer", location="New York, NY", job_description="ML & Python")
    job, _ = await IngestionService.process_job_ingest(async_db, req)

    # Initial state should be OFF
    state_rec = await OutreachService.get_or_create_state(async_db, job.id)
    assert state_rec.state == "OFF"

    # Enable outreach
    enabled_state = await OutreachService.enable_outreach(async_db, job.id)
    assert enabled_state.state in ["ENABLED", "CHOOSING_CONTACT"]

    # Disable outreach
    disabled_state = await OutreachService.disable_outreach(async_db, job.id)
    assert disabled_state.state == "OFF"

@pytest.mark.asyncio
async def test_contact_import_and_selection(async_db: AsyncSession):
    req = JobIngestRequest(company="Notion", title="AI Engineer", location="New York, NY", job_description="ML & Python")
    job, _ = await IngestionService.process_job_ingest(async_db, req)

    # Enable outreach
    await OutreachService.enable_outreach(async_db, job.id)

    # Option B: Import Contact
    import_req = ContactImportRequest(
        name="John Smith",
        company="Notion",
        title="Engineering Manager",
        profile_url="https://linkedin.com/in/johnsmith",
        email="john@notion.so",
        relationship="NYU alumni"
    )
    imported = await ContactService.import_contact(async_db, import_req)
    assert imported.name == "John Smith"
    assert imported.relationship == "NYU alumni"

    # Select contact for job
    state = await OutreachService.select_contact_for_job(async_db, job.id, imported.id)
    assert state.state == "CONTACT_SELECTED"
    assert state.selected_contact_id == imported.id

@pytest.mark.asyncio
async def test_message_generation_sent_tracking_and_followup(async_db: AsyncSession):
    req = JobIngestRequest(company="Notion", title="AI Engineer", location="New York, NY", job_description="ML & Python")
    job, _ = await IngestionService.process_job_ingest(async_db, req)

    # Import and select contact
    import_req = ContactImportRequest(
        name="Sarah Chen",
        company="Notion",
        title="Engineering Manager - AI",
        profile_url="https://linkedin.com/in/sarahchen"
    )
    contact = await ContactService.import_contact(async_db, import_req)
    await OutreachService.select_contact_for_job(async_db, job.id, contact.id)

    # Generate draft message
    state = await OutreachService.generate_draft_message(async_db, job.id, contact_id=contact.id, channel="LinkedIn", purpose="Introduce myself")
    assert state.state == "DRAFT_READY"
    assert state.current_draft is not None
    assert len(state.current_draft) > 10

    # Mark as sent
    event = await OutreachService.mark_sent(async_db, job.id, channel="LinkedIn")
    assert event.status == "sent"
    assert event.contact_id == contact.id
    
    refreshed_state = await OutreachService.get_or_create_state(async_db, job.id)
    assert refreshed_state.state == "SENT"

    # Generate follow-up draft
    followup_state = await OutreachService.generate_followup_draft(async_db, job.id, notes="Check in on team application")
    assert followup_state.state in ["FOLLOW_UP_AVAILABLE", "DRAFT_READY"]
    assert followup_state.current_draft is not None
