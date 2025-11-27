from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Organization
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Organization)

    async def get_by_name(self, name: str) -> Optional[Organization]:
        stmt = select(Organization).where(Organization.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active(self, skip: int = 0, limit: int = 100) -> List[Organization]:
        stmt = select(Organization).where(
            Organization.is_active == True
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Organization]:
        stmt = select(Organization).where(
            (Organization.name.ilike(f"%{query}%")) |
            (Organization.description.ilike(f"%{query}%"))
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_members(self, organization_id: UUID) -> int:
        from app.models import OrganizationMember
        stmt = select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
