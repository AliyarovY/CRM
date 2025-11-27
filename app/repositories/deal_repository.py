from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from decimal import Decimal

from app.models import Deal, DealStatusEnum
from app.repositories.base import BaseRepository


class DealRepository(BaseRepository[Deal]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Deal)

    async def list_by_organization(
        self, organization_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Deal]:
        stmt = select(Deal).where(
            Deal.organization_id == organization_id
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_contact(
        self, contact_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Deal]:
        stmt = select(Deal).where(
            Deal.contact_id == contact_id
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_status(
        self, organization_id: UUID, status: DealStatusEnum, skip: int = 0, limit: int = 100
    ) -> List[Deal]:
        stmt = select(Deal).where(
            and_(
                Deal.organization_id == organization_id,
                Deal.status == status
            )
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_assigned_to(
        self, organization_id: UUID, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Deal]:
        stmt = select(Deal).where(
            and_(
                Deal.organization_id == organization_id,
                Deal.assigned_to == user_id
            )
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search_by_organization(
        self, organization_id: UUID, query: str, skip: int = 0, limit: int = 100
    ) -> List[Deal]:
        stmt = select(Deal).where(
            and_(
                Deal.organization_id == organization_id,
                Deal.title.ilike(f"%{query}%")
            )
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_total_amount_by_organization(self, organization_id: UUID) -> Decimal:
        stmt = select(func.sum(Deal.amount)).where(
            and_(
                Deal.organization_id == organization_id,
                Deal.status.in_([DealStatusEnum.WON])
            )
        )
        result = await self.session.execute(stmt)
        total = result.scalar()
        return total or Decimal(0)

    async def get_total_amount_by_status(
        self, organization_id: UUID, status: DealStatusEnum
    ) -> Decimal:
        stmt = select(func.sum(Deal.amount)).where(
            and_(
                Deal.organization_id == organization_id,
                Deal.status == status
            )
        )
        result = await self.session.execute(stmt)
        total = result.scalar()
        return total or Decimal(0)

    async def count_by_organization(self, organization_id: UUID) -> int:
        stmt = select(Deal).where(
            Deal.organization_id == organization_id
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def count_by_status(
        self, organization_id: UUID, status: DealStatusEnum
    ) -> int:
        stmt = select(Deal).where(
            and_(
                Deal.organization_id == organization_id,
                Deal.status == status
            )
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
