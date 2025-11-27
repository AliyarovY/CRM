from uuid import UUID
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Activity, ActivityTypeEnum
from app.repositories import ActivityRepository
from app.core.exceptions import NotFound


class ActivityService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.activity_repo = ActivityRepository(session)

    async def create_activity(
        self,
        organization_id: UUID,
        activity_type: ActivityTypeEnum,
        created_by: UUID,
        title: str,
        description: Optional[str] = None,
        contact_id: Optional[UUID] = None,
        deal_id: Optional[UUID] = None,
        activity_date: Optional[datetime] = None,
    ) -> Activity:
        activity = Activity(
            organization_id=organization_id,
            contact_id=contact_id,
            deal_id=deal_id,
            created_by=created_by,
            activity_type=activity_type,
            title=title,
            description=description,
            activity_date=activity_date or datetime.utcnow(),
        )
        return await self.activity_repo.create(activity)

    async def get_activity(self, activity_id: UUID) -> Optional[Activity]:
        return await self.activity_repo.get(activity_id)

    async def list_activities(
        self, organization_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Activity]:
        return await self.activity_repo.list_by_organization(organization_id, skip, limit)

    async def list_contact_activities(
        self, contact_id: UUID, limit: int = 10
    ) -> List[Activity]:
        return await self.activity_repo.get_recent_by_contact(contact_id, limit)

    async def list_deal_activities(
        self, deal_id: UUID, limit: int = 10
    ) -> List[Activity]:
        return await self.activity_repo.get_recent_by_deal(deal_id, limit)

    async def list_user_activities(
        self,
        organization_id: UUID,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Activity]:
        return await self.activity_repo.list_by_created_by(
            organization_id, user_id, skip, limit
        )

    async def log_call(
        self,
        organization_id: UUID,
        created_by: UUID,
        title: str,
        description: Optional[str] = None,
        contact_id: Optional[UUID] = None,
        deal_id: Optional[UUID] = None,
    ) -> Activity:
        return await self.create_activity(
            organization_id=organization_id,
            activity_type=ActivityTypeEnum.CALL,
            created_by=created_by,
            title=title,
            description=description,
            contact_id=contact_id,
            deal_id=deal_id,
        )

    async def log_email(
        self,
        organization_id: UUID,
        created_by: UUID,
        title: str,
        description: Optional[str] = None,
        contact_id: Optional[UUID] = None,
        deal_id: Optional[UUID] = None,
    ) -> Activity:
        return await self.create_activity(
            organization_id=organization_id,
            activity_type=ActivityTypeEnum.EMAIL,
            created_by=created_by,
            title=title,
            description=description,
            contact_id=contact_id,
            deal_id=deal_id,
        )

    async def log_meeting(
        self,
        organization_id: UUID,
        created_by: UUID,
        title: str,
        description: Optional[str] = None,
        contact_id: Optional[UUID] = None,
        deal_id: Optional[UUID] = None,
        activity_date: Optional[datetime] = None,
    ) -> Activity:
        return await self.create_activity(
            organization_id=organization_id,
            activity_type=ActivityTypeEnum.MEETING,
            created_by=created_by,
            title=title,
            description=description,
            contact_id=contact_id,
            deal_id=deal_id,
            activity_date=activity_date,
        )

    async def log_note(
        self,
        organization_id: UUID,
        created_by: UUID,
        title: str,
        description: Optional[str] = None,
        contact_id: Optional[UUID] = None,
        deal_id: Optional[UUID] = None,
    ) -> Activity:
        return await self.create_activity(
            organization_id=organization_id,
            activity_type=ActivityTypeEnum.NOTE,
            created_by=created_by,
            title=title,
            description=description,
            contact_id=contact_id,
            deal_id=deal_id,
        )

    async def get_recent_activities(
        self, organization_id: UUID, limit: int = 20
    ) -> List[Activity]:
        return await self.activity_repo.get_recent_by_organization(organization_id, limit)

    async def count_activities(self, organization_id: UUID) -> int:
        return await self.activity_repo.count_by_organization(organization_id)
