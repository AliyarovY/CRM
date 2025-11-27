from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models import Contact
from app.repositories.base import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Contact)

    async def list_by_organization(
        self, organization_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Contact]:
        stmt = select(Contact).where(
            Contact.organization_id == organization_id
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_active_by_organization(
        self, organization_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Contact]:
        stmt = select(Contact).where(
            and_(
                Contact.organization_id == organization_id,
                Contact.is_active == True
            )
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search_by_organization(
        self, organization_id: UUID, query: str, skip: int = 0, limit: int = 100
    ) -> List[Contact]:
        stmt = select(Contact).where(
            and_(
                Contact.organization_id == organization_id,
                (
                    (Contact.first_name.ilike(f"%{query}%")) |
                    (Contact.last_name.ilike(f"%{query}%")) |
                    (Contact.email.ilike(f"%{query}%")) |
                    (Contact.phone.ilike(f"%{query}%")) |
                    (Contact.company.ilike(f"%{query}%"))
                )
            )
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_email(self, organization_id: UUID, email: str) -> Optional[Contact]:
        stmt = select(Contact).where(
            and_(
                Contact.organization_id == organization_id,
                Contact.email == email
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_company(
        self, organization_id: UUID, company: str, skip: int = 0, limit: int = 100
    ) -> List[Contact]:
        stmt = select(Contact).where(
            and_(
                Contact.organization_id == organization_id,
                Contact.company == company
            )
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_organization(self, organization_id: UUID) -> int:
        stmt = select(Contact).where(
            Contact.organization_id == organization_id
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
