from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.models import Contact

class ContactRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, contact_id: int) -> Optional[Contact]:
        res = await db.execute(select(Contact).where(Contact.id == contact_id))
        return res.scalar_one_or_none()

    @staticmethod
    async def list_contacts(
        db: AsyncSession,
        company: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 50
    ) -> List[Contact]:
        stmt = select(Contact)
        if company:
            # Case-insensitive company filter
            stmt = stmt.where(Contact.company.ilike(f"%{company.strip()}%"))
        if query:
            q_clean = f"%{query.strip()}%"
            stmt = stmt.where(
                or_(
                    Contact.name.ilike(q_clean),
                    Contact.title.ilike(q_clean),
                    Contact.company.ilike(q_clean),
                    Contact.relationship.ilike(q_clean)
                )
            )
        stmt = stmt.order_by(Contact.overall_score.desc()).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def save_contact(db: AsyncSession, contact: Contact) -> Contact:
        db.add(contact)
        await db.flush()
        return contact
