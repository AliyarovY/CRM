from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models import Activity, ActivityTypeEnum
from app.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Activity)

    async def list_by_organization(
        self, organization_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Activity]:
        stmt = select(Activity).where(
            Activity.organization_id == organization_id
        ).order_by(desc(Activity.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_contact(
        self, contact_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Activity]:
        stmt = select(Activity).where(
            Activity.contact_id == contact_id
        ).order_by(desc(Activity.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_deal(
        self, deal_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Activity]:
        stmt = select(Activity).where(
            Activity.deal_id == deal_id
        ).order_by(desc(Activity.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_created_by(
        self, organization_id: UUID, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Activity]:
        stmt = select(Activity).where(
            and_(
                Activity.organization_id == organization_id,
                Activity.created_by == user_id
            )
        ).order_by(desc(Activity.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_type(
        self, organization_id: UUID, activity_type: ActivityTypeEnum, skip: int = 0, limit: int = 100
    ) -> List[Activity]:
        stmt = select(Activity).where(
            and_(
                Activity.organization_id == organization_id,
                Activity.activity_type == activity_type
            )
        ).order_by(desc(Activity.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_recent_by_organization(
        self, organization_id: UUID, limit: int = 10
    ) -> List[Activity]:
        stmt = select(Activity).where(
            Activity.organization_id == organization_id
        ).order_by(desc(Activity.created_at)).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_recent_by_contact(
        self, contact_id: UUID, limit: int = 10
    ) -> List[Activity]:
        stmt = select(Activity).where(
            Activity.contact_id == contact_id
        ).order_by(desc(Activity.created_at)).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_recent_by_deal(
        self, deal_id: UUID, limit: int = 10
    ) -> List[Activity]:
        stmt = select(Activity).where(
            Activity.deal_id == deal_id
        ).order_by(desc(Activity.created_at)).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_organization(self, organization_id: UUID) -> int:
        stmt = select(Activity).where(
            Activity.organization_id == organization_id
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def count_by_type(
        self, organization_id: UUID, activity_type: ActivityTypeEnum
    ) -> int:
        stmt = select(Activity).where(
            and_(
                Activity.organization_id == organization_id,
                Activity.activity_type == activity_type
            )
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
