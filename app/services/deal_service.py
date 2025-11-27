from uuid import UUID
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Deal, DealStatusEnum, Activity, ActivityTypeEnum
from app.repositories import DealRepository, ActivityRepository
from app.core.exceptions import NotFound, BadRequest


class DealService:
    VALID_STATUS_TRANSITIONS = {
        DealStatusEnum.NEW: [DealStatusEnum.IN_PROGRESS, DealStatusEnum.LOST],
        DealStatusEnum.IN_PROGRESS: [DealStatusEnum.WON, DealStatusEnum.LOST],
        DealStatusEnum.WON: [],
        DealStatusEnum.LOST: [],
        DealStatusEnum.CLOSED: [],
    }

    def __init__(self, session: AsyncSession):
        self.session = session
        self.deal_repo = DealRepository(session)
        self.activity_repo = ActivityRepository(session)

    async def create_deal(
        self,
        organization_id: UUID,
        contact_id: UUID,
        title: str,
        assigned_to: Optional[UUID] = None,
        description: Optional[str] = None,
        amount: Optional[Decimal] = None,
        expected_close_date: Optional[datetime] = None,
    ) -> Deal:
        if amount is not None and amount <= 0:
            raise BadRequest("Deal amount must be greater than 0")

        deal = Deal(
            organization_id=organization_id,
            contact_id=contact_id,
            assigned_to=assigned_to,
            title=title,
            description=description,
            amount=amount,
            expected_close_date=expected_close_date,
        )
        return await self.deal_repo.create(deal)

    async def get_deal(self, deal_id: UUID) -> Optional[Deal]:
        return await self.deal_repo.get(deal_id)

    async def list_deals(
        self, organization_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Deal]:
        return await self.deal_repo.list_by_organization(organization_id, skip, limit)

    async def update_deal(
        self, deal_id: UUID, updates: dict
    ) -> Optional[Deal]:
        deal = await self.deal_repo.get(deal_id)
        if deal is None:
            raise NotFound("Deal not found")

        if "amount" in updates and updates["amount"] is not None:
            if updates["amount"] <= 0:
                raise BadRequest("Deal amount must be greater than 0")

        return await self.deal_repo.update(deal_id, updates)

    async def change_deal_status(
        self,
        deal_id: UUID,
        new_status: DealStatusEnum,
        user_id: UUID,
    ) -> Optional[Deal]:
        deal = await self.deal_repo.get(deal_id)
        if deal is None:
            raise NotFound("Deal not found")

        current_status = deal.status
        if new_status not in self.VALID_STATUS_TRANSITIONS.get(current_status, []):
            raise BadRequest(
                f"Cannot transition from {current_status} to {new_status}"
            )

        if new_status == DealStatusEnum.WON:
            if deal.amount is None or deal.amount <= 0:
                raise BadRequest(
                    "Deal must have amount > 0 to be marked as won"
                )
            deal.closed_date = datetime.utcnow()

        if new_status == DealStatusEnum.LOST:
            deal.closed_date = datetime.utcnow()

        deal.status = new_status
        await self.session.commit()
        await self.session.refresh(deal)

        activity = Activity(
            organization_id=deal.organization_id,
            deal_id=deal_id,
            created_by=user_id,
            activity_type=ActivityTypeEnum.NOTE,
            title=f"Deal status changed to {new_status}",
            description=f"Status changed from {current_status} to {new_status}",
        )
        await self.activity_repo.create(activity)

        return deal

    async def delete_deal(self, deal_id: UUID) -> bool:
        deal = await self.deal_repo.get(deal_id)
        if deal is None:
            raise NotFound("Deal not found")

        return await self.deal_repo.delete(deal_id)

    async def search_deals(
        self,
        organization_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Deal]:
        return await self.deal_repo.search_by_organization(
            organization_id, query, skip, limit
        )

    async def get_deals_by_status(
        self,
        organization_id: UUID,
        status: DealStatusEnum,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Deal]:
        return await self.deal_repo.list_by_status(organization_id, status, skip, limit)

    async def get_total_won_amount(self, organization_id: UUID) -> Decimal:
        return await self.deal_repo.get_total_amount_by_organization(organization_id)

    async def get_deal_count(self, organization_id: UUID) -> int:
        return await self.deal_repo.count_by_organization(organization_id)
