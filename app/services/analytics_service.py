from uuid import UUID
from typing import Dict, List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DealStatusEnum, TaskStatusEnum, ActivityTypeEnum
from app.repositories import DealRepository, TaskRepository, ContactRepository, ActivityRepository


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.deal_repo = DealRepository(session)
        self.task_repo = TaskRepository(session)
        self.contact_repo = ContactRepository(session)
        self.activity_repo = ActivityRepository(session)

    async def get_deals_summary(self, organization_id: UUID) -> Dict[str, any]:
        total = await self.deal_repo.count_by_organization(organization_id)

        new_count = await self.deal_repo.count_by_status(organization_id, DealStatusEnum.NEW)
        in_progress_count = await self.deal_repo.count_by_status(
            organization_id, DealStatusEnum.IN_PROGRESS
        )
        won_count = await self.deal_repo.count_by_status(organization_id, DealStatusEnum.WON)
        lost_count = await self.deal_repo.count_by_status(organization_id, DealStatusEnum.LOST)

        won_amount = await self.deal_repo.get_total_amount_by_organization(organization_id)

        pipeline_amount = (
            await self.deal_repo.get_total_amount_by_status(
                organization_id, DealStatusEnum.IN_PROGRESS
            )
        )

        return {
            "total_deals": total,
            "new": new_count,
            "in_progress": in_progress_count,
            "won": won_count,
            "lost": lost_count,
            "won_amount": won_amount,
            "pipeline_amount": pipeline_amount,
            "win_rate": round((won_count / total * 100) if total > 0 else 0, 2),
        }

    async def get_tasks_summary(self, organization_id: UUID) -> Dict[str, any]:
        total = await self.task_repo.count_by_organization(organization_id)

        todo_count = await self.task_repo.count_by_status(organization_id, TaskStatusEnum.TODO)
        in_progress_count = await self.task_repo.count_by_status(
            organization_id, TaskStatusEnum.IN_PROGRESS
        )
        done_count = await self.task_repo.count_by_status(organization_id, TaskStatusEnum.DONE)

        overdue = await self.task_repo.list_overdue(organization_id, 0, 1000)

        return {
            "total_tasks": total,
            "todo": todo_count,
            "in_progress": in_progress_count,
            "done": done_count,
            "overdue": len(overdue),
            "completion_rate": round((done_count / total * 100) if total > 0 else 0, 2),
        }

    async def get_contact_statistics(self, organization_id: UUID) -> Dict[str, any]:
        total_contacts = await self.contact_repo.count_by_organization(organization_id)

        return {
            "total_contacts": total_contacts,
        }

    async def get_activity_statistics(self, organization_id: UUID) -> Dict[str, any]:
        total = await self.activity_repo.count_by_organization(organization_id)

        calls = await self.activity_repo.count_by_type(
            organization_id, ActivityTypeEnum.CALL
        )
        emails = await self.activity_repo.count_by_type(
            organization_id, ActivityTypeEnum.EMAIL
        )
        meetings = await self.activity_repo.count_by_type(
            organization_id, ActivityTypeEnum.MEETING
        )
        notes = await self.activity_repo.count_by_type(
            organization_id, ActivityTypeEnum.NOTE
        )

        return {
            "total_activities": total,
            "calls": calls,
            "emails": emails,
            "meetings": meetings,
            "notes": notes,
        }

    async def get_dashboard_summary(self, organization_id: UUID) -> Dict[str, any]:
        deals_summary = await self.get_deals_summary(organization_id)
        tasks_summary = await self.get_tasks_summary(organization_id)
        contacts_stats = await self.get_contact_statistics(organization_id)
        activity_stats = await self.get_activity_statistics(organization_id)
        recent_activities = await self.activity_repo.get_recent_by_organization(
            organization_id, 10
        )

        return {
            "deals": deals_summary,
            "tasks": tasks_summary,
            "contacts": contacts_stats,
            "activities": activity_stats,
            "recent_activities": [
                {
                    "id": str(a.id),
                    "title": a.title,
                    "type": a.activity_type,
                    "created_at": a.created_at,
                }
                for a in recent_activities
            ],
        }
