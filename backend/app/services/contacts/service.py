import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Contact
from app.schemas.schemas import ContactImportRequest
from app.services.contacts.repository import ContactRepository

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)

class ContactService:
    @staticmethod
    async def import_contact(db: AsyncSession, req: ContactImportRequest) -> Contact:
        contact = Contact(
            name=req.name.strip(),
            company=req.company.strip(),
            title=req.title.strip(),
            relationship=req.relationship or "Imported contact",
            linkedin_url=req.profile_url,
            email=req.email,
            source="User Import",
            company_verified=True,
            role_verified=True,
            verification_confidence=1.0,
            last_verified_at=utcnow(),
            overall_score=90
        )
        saved = await ContactRepository.save_contact(db, contact)
        await db.commit()
        await db.refresh(saved)
        return saved

    @staticmethod
    async def get_contacts(
        db: AsyncSession,
        company: Optional[str] = None,
        query: Optional[str] = None
    ) -> List[Contact]:
        return await ContactRepository.list_contacts(db, company=company, query=query)

    @staticmethod
    async def get_by_id(db: AsyncSession, contact_id: int) -> Optional[Contact]:
        return await ContactRepository.get_by_id(db, contact_id)
